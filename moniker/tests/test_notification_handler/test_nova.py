# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from moniker.openstack.common import log as logging
from moniker.notification_handler.nova import NovaFixedHandler
from moniker.tests.test_notification_handler import NotificationHandlerTestCase

LOG = logging.getLogger(__name__)


class NovaFixedHandlerTest(NotificationHandlerTestCase):
    __test__ = True

    def setUp(self):
        super(NovaFixedHandlerTest, self).setUp()

        domain = self.create_domain()
        self.domain_id = domain['id']
        self.config(domain_id=domain['id'], group='handler:nova_fixed')

        self.plugin = NovaFixedHandler()

    def test_instance_create_end(self):
        event_type = 'compute.instance.create.end'
        fixture = self.get_notification_fixture('nova', event_type)

        self.assertIn(event_type, self.plugin.get_event_types())

        # Ensure we start with 0 records
        records = self.central_service.get_records(self.admin_context,
                                                   self.domain_id)

        self.assertEqual(0, len(records))

        self.plugin.process_notification(event_type, fixture['payload'])

        # Ensure we now have exactly 1 record
        records = self.central_service.get_records(self.admin_context,
                                                   self.domain_id)

        self.assertEqual(len(records), 1)

    def test_instance_delete_start(self):
        # Prepare for the test
        start_event_type = 'compute.instance.create.end'
        start_fixture = self.get_notification_fixture('nova', start_event_type)

        self.plugin.process_notification(start_event_type,
                                         start_fixture['payload'])

        # Now - Onto the real test
        event_type = 'compute.instance.delete.start'
        fixture = self.get_notification_fixture('nova', event_type)

        self.assertIn(event_type, self.plugin.get_event_types())

        # Ensure we start with at least 1 record
        records = self.central_service.get_records(self.admin_context,
                                                   self.domain_id)

        self.assertGreaterEqual(len(records), 1)

        self.plugin.process_notification(event_type, fixture['payload'])

        # Ensure we now have exactly 0 records
        records = self.central_service.get_records(self.admin_context,
                                                   self.domain_id)

        self.assertEqual(0, len(records))
