from typing import Any


class RangePicker:

    def __init__(self, values: dict[float, Any]) -> None:
        self.values = {range_val: values[range_val] for range_val in sorted(values.keys())}

    def __getitem__(self, range_val: float) -> float:
        size_ranges: list[tuple[float, Any]] = list(self.values.items())


        if range_val < size_ranges[0][0]: return size_ranges[0][1]
        if range_val > size_ranges[-1][0]: return size_ranges[-1][1]

        for i, (range_, value) in enumerate(size_ranges[:-1]):
            if range_val >= range_ and range_val <= size_ranges[i + 1][0]:
                return value
            
if __name__ == "__main__":
    range_picker: RangePicker = RangePicker({
        10: "a",
        13: "b",
        15: "c"
    })

    for i in range(20):
        print(i, range_picker[i])
            