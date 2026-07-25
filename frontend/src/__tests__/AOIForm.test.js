import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AOIPanel from "../AOIForm";
import { add_box_AOI } from "../utils";

jest.mock("../utils", () => ({
    add_box_AOI: jest.fn(),
}));

describe("AOIPanel", () => {

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test("renders all inputs", () => {
        render(<AOIPanel />);

        expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Description")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Lat Min")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Lat Max")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Long Min")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Long Max")).toBeInTheDocument();
    });

    test("submits correct values", async () => {

        add_box_AOI.mockResolvedValue({ success: true });

        render(<AOIPanel />);

        await userEvent.type(screen.getByPlaceholderText("Name"), "Singapore");

        await userEvent.type(screen.getByPlaceholderText("Description"), "Port");

        await userEvent.type(screen.getByPlaceholderText("Lat Min"), "1");

        await userEvent.type(screen.getByPlaceholderText("Lat Max"), "2");

        await userEvent.type(screen.getByPlaceholderText("Long Min"), "103");

        await userEvent.type(screen.getByPlaceholderText("Long Max"), "104");

        await userEvent.click(screen.getByRole("button", { name: /add aoi/i }));

        await waitFor(() => {
            expect(add_box_AOI).toHaveBeenCalledWith({
                name: "Singapore",
                desc: "Port",
                lat_min: 1,
                lat_max: 2,
                long_min: 103,
                long_max: 104,
            });
        });

        expect(add_box_AOI).toHaveBeenCalledWith({
            name: "Singapore",
            desc: "Port",
            lat_min: 1,
            lat_max: 2,
            long_min: 103,
            long_max: 104,
        });
    });

});
