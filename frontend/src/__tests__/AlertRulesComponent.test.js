jest.mock("../AlertRuleForm", () => () => (
    <div>FORM</div>
));

jest.mock("../AlertRulesDisplay", () => (props) => (
    <>
        <div>LIST</div>

        <button
            onClick={() =>
                props.onEdit({
                    alert_rule_id: 1
                })
            }
        >
            Edit
        </button>
    </>
));

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import AlertRulesComponent from "../AlertRulesComponent";

test("renders form and list", () => {

    render(<AlertRulesComponent />);

    expect(screen.getByText("FORM")).toBeInTheDocument();
    expect(screen.getByText("LIST")).toBeInTheDocument();

});

test("edit button works", async () => {

    const user = userEvent.setup();

    render(<AlertRulesComponent />);

    await user.click(
        screen.getByText("Edit")
    );

});
