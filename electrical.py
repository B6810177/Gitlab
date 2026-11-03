import json
import math


def equivalent_resistance(network):
    if isinstance(network, bool):
        raise ValueError("Resistance must be a positive number")

    if isinstance(network, (int, float)):
        resistance = float(network)
        if not math.isfinite(resistance) or resistance <= 0:
            raise ValueError("Resistance must be a positive finite number")
        return resistance

    if not isinstance(network, dict) or len(network) != 1:
        raise ValueError("A network must be a resistance or a series/parallel object")

    connection, components = next(iter(network.items()))
    if connection not in ("series", "parallel"):
        raise ValueError("Connection must be 'series' or 'parallel'")
    if not isinstance(components, list) or not components:
        raise ValueError("A connection must contain a non-empty list of components")

    resistances = [equivalent_resistance(component) for component in components]
    if connection == "series":
        return sum(resistances)
    return 1 / sum(1 / resistance for resistance in resistances)


def analyze_dc(voltage_v, resistance_ohm):
    if isinstance(voltage_v, bool):
        raise ValueError("Voltage must be a finite number")
    try:
        voltage_v = float(voltage_v)
    except (TypeError, ValueError) as error:
        raise ValueError("Voltage must be a finite number") from error
    if not math.isfinite(voltage_v):
        raise ValueError("Voltage must be a finite number")

    resistance_ohm = equivalent_resistance(resistance_ohm)
    current_a = voltage_v / resistance_ohm
    power_w = voltage_v * current_a
    return {"current_a": current_a, "power_w": power_w}


def main():
    print("DC Circuit Calculator")
    print("Choose: 1) single  2) series  3) parallel  4) mixed (JSON)")
    choice = input("Circuit type: ").strip()
    if choice not in ("1", "2", "3", "4"):
        raise ValueError("Choose a circuit type from 1 to 4")

    voltage_v = float(input("Voltage (V): ").strip())
    if choice == "4":
        print('Enter a JSON network, e.g. {"series": [10, {"parallel": [20, 30]}]}')
        network = json.loads(input("Network: "))
    else:
        raw_resistances = input("Resistance(s) in ohms (comma-separated): ").strip()
        resistances = [float(value.strip()) for value in raw_resistances.split(",")]
        if choice == "1" and len(resistances) != 1:
            raise ValueError("Single circuit requires exactly one resistance")
        network = resistances[0] if choice == "1" else {
            "series" if choice == "2" else "parallel": resistances
        }

    resistance = equivalent_resistance(network)
    result = analyze_dc(voltage_v, resistance)
    print(f"Equivalent resistance: {resistance:.6g} ohm")
    print(f"Current: {result['current_a']:.6g} A")
    print(f"Power: {result['power_w']:.6g} W")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"Error: {error}")