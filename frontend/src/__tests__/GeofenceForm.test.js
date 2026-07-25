import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GeofencePanel from "../GeofenceForm";
import { add_box_geofence } from "../utils";

jest.mock("../utils", () => ({
    add_box_geofence: jest.fn(),
}));

describe("GeofencePanel", () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("submits geofence", async () => {

        const user = userEvent.setup();

        add_box_geofence.mockResolvedValue({ success: true });

        render(<GeofencePanel />);

        await user.type(screen.getByPlaceholderText("Name"), "Harbour");
        await user.type(screen.getByPlaceholderText("Lat Min"), "1");
        await user.type(screen.getByPlaceholderText("Lat Max"), "2");
        await user.type(screen.getByPlaceholderText("Long Min"), "3");
        await user.type(screen.getByPlaceholderText("Long Max"), "4");

        await user.click(
            screen.getByRole("button", {
                name: /add geofence/i,
            })
        );

        await waitFor(() => {

            expect(add_box_geofence).toHaveBeenCalled();

        });

    });

});
