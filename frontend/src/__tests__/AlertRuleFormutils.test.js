import { convertRule, parseRule } from "../AlertRuleForm";

describe("convertRule", () => {

    test("converts speed rule", () => {

        expect(convertRule({
            field: "speed",
            operator: ">",
            value: "15"
        })).toEqual({
            field: "speed",
            operator: ">",
            value: 15
        });

    });

    test("converts ship name rule", () => {

        expect(convertRule({
            field: "shipname",
            operator: "=",
            value: "Ever Given"
        })).toEqual({
            field: "shipname",
            operator: "=",
            value: "Ever Given"
        });

    });

    test("converts geofence rule", () => {

        expect(convertRule({
            field: "inside_geofence",
            operator: "=",
            value: JSON.stringify({
                geofenceId: 12
            })
        })).toEqual({
            field: "inside_geofence",
            operator: "=",
            value: true,
            valueGeofenceid: 12
        });

    });

    test("converts proximity rule", () => {

        expect(convertRule({
            field: "proximity_to_shipname",
            operator: "=",
            value: JSON.stringify({
                distance: 500,
                shipname: "Ever Given"
            })
        })).toEqual({
            field: "proximity_to_shipname",
            operator: "=",
            value: 500,
            valueShipname: "Ever Given"
        });

    });

});

describe("parseRule", () => {

    test("parses speed rule", () => {

        const parsed = parseRule({
            field: "speed",
            operator: ">",
            value: 20
        });

        expect(parsed.rules[0].field).toBe("speed");
        expect(parsed.rules[0].value).toBe("20");

    });

    test("parses geofence rule", () => {

        const parsed = parseRule({
            field: "inside_geofence",
            operator: "=",
            valueGeofenceid: 7
        });

        expect(
            JSON.parse(parsed.rules[0].value)
        ).toEqual({
            geofenceId: 7
        });

    });

});
