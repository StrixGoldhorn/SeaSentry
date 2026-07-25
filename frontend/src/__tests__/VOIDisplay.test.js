import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import VOIList from "../VOIDisplay";
import { get_all_VOI, delete_VOI } from "../utils";

jest.mock("../utils", () => ({
    get_all_VOI: jest.fn(),
    delete_VOI: jest.fn(),
}));

describe("VOIList", () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("loads vessels", async () => {

        get_all_VOI.mockResolvedValue({

            data: [

                {
                    vessel_of_interest_id: 1,
                    vessel_of_interest_desc_name: "Ever Given",
                    vessel_of_interest_description: "Cargo",
                    vessel_of_interest_mmsi: "123",
                    vessel_of_interest_imo: "456",
                }

            ]

        });

        render(<VOIList />);

        expect(
            await screen.findByText("Ever Given")
        ).toBeInTheDocument();

    });

    test("shows empty message", async () => {

        get_all_VOI.mockResolvedValue({
            data: [],
        });

        render(<VOIList />);

        expect(
            await screen.findByText(/no vessels of interest/i)
        ).toBeInTheDocument();

    });

    test("calls delete", async () => {

        const user = userEvent.setup();

        window.confirm = jest.fn(() => true);

        get_all_VOI.mockResolvedValue({

            data: [

                {
                    vessel_of_interest_id: 1,
                    vessel_of_interest_desc_name: "Ever Given",
                }

            ]

        });

        delete_VOI.mockResolvedValue({});

        render(<VOIList />);

        await user.click(
            await screen.findByRole("button", {
                name: /delete/i,
            })
        );

        await waitFor(() => {

            expect(delete_VOI).toHaveBeenCalled();

        });

    });

});
