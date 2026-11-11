# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


class TestAiTool(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "AI Tool User",
                    "login": "ai_tool_user",
                    "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
                }
            )
        )

    def test_tool_as_user(self):
        """Users without access to the models (ir.model) can use the tools"""
        tool = self.env.ref("ai_tool.current_date").with_user(self.user)
        definition = tool._get_tool_definition()
        self.assertEqual(definition["inputSchema"]["type"], "object")
        with freeze_time("2024-01-01"):
            self.assertEqual(tool._execute_tool(record=tool)["date"], "2024-01-01")

    def test_tool(self):
        definition = self.env.ref("ai_tool.current_date")._get_tool_definition()
        self.assertEqual(definition["inputSchema"]["type"], "object")
        self.assertEqual(definition["outputSchema"]["type"], "object")

    def test_get_date_tool(self):
        with freeze_time("2024-01-01"):
            tool = self.env.ref("ai_tool.current_date")
            result = tool._execute_tool(record=tool)
            self.assertEqual(result["date"], "2024-01-01")

    def test_post_message_tool(self):
        partner = self.partner
        messages = partner.message_ids
        tool = self.env.ref("ai_tool.post_message")
        tool._execute_tool(message="Hello World", record=partner)
        self.assertEqual(len(partner.message_ids), len(messages) + 1)
        self.assertRegex((partner.message_ids - messages).body, "Hello World")

    def test_tool_no_record(self):
        tool = self.env.ref("ai_tool.post_message")
        with self.assertRaises(ValueError):
            tool._execute_tool(message="Hello World")

    def test_post_message_tool_no_record(self):
        tool = self.env.ref("ai_tool.post_message")
        tool.kind = "generic"
        with self.assertRaises(ValueError):
            tool._execute_tool(message="Hello World", record=self.partner)

    def test_post_message_tool_record_different_model(self):
        tool = self.env.ref("ai_tool.post_message")
        tool.kind = "record"
        with self.assertRaises(ValueError):
            tool._execute_tool(message="Hello World", record=self.partner)
