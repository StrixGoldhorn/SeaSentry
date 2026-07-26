import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import VOIPanel from "../VOIForm";
import { add_VOI, update_VOI } from "../utils";

jest.mock("../utils", () => ({
    add_VOI: jest.fn(),
    update_VOI: jest.fn(),
}));

describe("VOIPanel", () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("shows add mode", () => {

        render(<VOIPanel />);

        expect(
            screen.getByText(/add vessel of interest/i)
        ).toBeInTheDocument();

    });

    test("shows edit mode", () => {

        render(

            <VOIPanel
                initialVOI={{
                    vessel_of_interest_id: 1,
                    vessel_of_interest_desc_name: "Ever Given",
                    vessel_of_interest_description: "Cargo",
                    vessel_of_interest_mmsi: "123",
                    vessel_of_interest_imo: "456",
                }}
            />

        );

        expect(
            screen.getByText(/edit vessel of interest/i)
        ).toBeInTheDocument();

        expect(
            screen.getByDisplayValue("Ever Given")
        ).toBeInTheDocument();

    });

    test("calls add_VOI", async () => {

        const user = userEvent.setup();

        add_VOI.mockResolvedValue({ success: true });

        render(<VOIPanel />);

        await user.type(
            screen.getByPlaceholderText("Name"),
            "Ever Given"
        );

        await user.type(
            screen.getByPlaceholderText("MMSI"),
            "123456789"
        );

        await user.click(
            screen.getByRole("button", {
                name: /add voi/i,
            })
        );

        await waitFor(() => {

            expect(add_VOI).toHaveBeenCalled();

        });

    });

    test("calls update_VOI", async () => {

        const user = userEvent.setup();

        update_VOI.mockResolvedValue({ success: true });

        render(

            <VOIPanel
                initialVOI={{
                    vessel_of_interest_id: 1,
                    vessel_of_interest_desc_name: "Ever Given",
                }}
            />

        );

        await user.click(
            screen.getByRole("button", {
                name: /edit voi/i,
            })
        );

        await waitFor(() => {

            expect(update_VOI).toHaveBeenCalled();

        });

    });

});
