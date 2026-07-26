import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AlertRulesList from "../AlertRulesDisplay";

import {
    get_all_alert_rules,
    enable_alert_rule,
    disable_alert_rule,
    delete_alert_rule,
} from "../utils";

jest.mock("../utils");

describe("AlertRulesList", () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("loads rules", async () => {

        get_all_alert_rules.mockResolvedValue({

            data: [

                {
                    alert_rule_id: 1,
                    alert_rule_name: "Speeding",
                    alert_rule_description: "Fast ship",
                    alert_rule_enabled: true,
                    alert_rule_params: {},
                }

            ]

        });

        render(<AlertRulesList />);

        expect(
            await screen.findByText("Speeding")
        ).toBeInTheDocument();

    });

});

test("disables enabled rule", async () => {

    const user = userEvent.setup();

    get_all_alert_rules.mockResolvedValue({

        data: [

            {
                alert_rule_id: 5,
                alert_rule_name: "Rule",
                alert_rule_enabled: true,
                alert_rule_params: {},
            }

        ]

    });

    disable_alert_rule.mockResolvedValue({});

    render(<AlertRulesList />);

    await user.click(
        await screen.findByRole("button", {
            name: /disable/i
        })
    );

    await waitFor(() => {

        expect(disable_alert_rule).toHaveBeenCalledWith({
            alert_rule_id: 5
        });

    });

});

test("deletes rule", async () => {

    const user = userEvent.setup();

    window.confirm = jest.fn(() => true);

    get_all_alert_rules.mockResolvedValue({

        data: [

            {
                alert_rule_id: 7,
                alert_rule_name: "Delete Me",
                alert_rule_enabled: true,
                alert_rule_params: {},
            }

        ]

    });

    delete_alert_rule.mockResolvedValue({});

    render(<AlertRulesList />);

    await user.click(
        await screen.findByRole("button", {
            name: /delete/i
        })
    );

    await waitFor(() => {

        expect(delete_alert_rule).toHaveBeenCalled();

    });

});
