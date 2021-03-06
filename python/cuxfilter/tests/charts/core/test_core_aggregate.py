import pytest
import pandas as pd
import numpy as np

from bokeh.models import ColumnDataSource
from cuxfilter.charts.core.aggregate.core_aggregate import BaseAggregateChart


class TestCoreAggregateChart:
    def test_variables(self):
        bac = BaseAggregateChart()

        # BaseChart variables
        assert bac.chart_type is None
        assert bac.x is None
        assert bac.y is None
        assert bac.aggregate_fn == "count"
        assert bac.color is None
        assert bac.height == 0
        assert bac.width == 0
        assert bac.add_interaction is True
        assert bac.chart is None
        assert bac.source is None
        assert bac.source_backup is None
        assert bac.data_points == 0
        assert bac._library_specific_params == {}
        assert bac._stride is None
        assert bac.stride_type == int
        assert bac.min_value == 0.0
        assert bac.max_value == 0.0
        assert bac.x_label_map == {}
        assert bac.y_label_map == {}

        bac.x = "test_x"
        bac.chart_type = "test_chart_type"

        assert bac.name == "test_x_test_chart_type"

        # BaseAggregateChart variables
        assert bac.use_data_tiles is True

    @pytest.mark.parametrize(
        "stride, _stride", [(1, 1), (None, None), (0.01, 0.01)]
    )
    def test_stride(self, stride, _stride):
        bac = BaseAggregateChart()
        bac.stride = stride
        assert bac._stride == _stride

    def test_label_mappers(self):
        bac = BaseAggregateChart()
        library_specific_params = {
            "x_label_map": {"a": 1, "b": 2},
            "y_label_map": {"a": 1, "b": 2},
        }
        bac.library_specific_params = library_specific_params

        assert bac.x_label_map == {"a": 1, "b": 2}
        assert bac.y_label_map == {"a": 1, "b": 2}

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bac = BaseAggregateChart()
        bac.chart = chart
        assert bac.view() == _chart

    @pytest.mark.parametrize(
        "query_tuple, result",
        [
            ((10, 13), [1.0, 1.0, 1.0, 1.0, 0.0]),
            ((10, 10), [1.0, 0.0, 0.0, 0.0, 0.0]),
            ((10, 12), [1.0, 1.0, 1.0, 0.0, 0.0]),
        ],
    )
    def test_query_chart_by_range(self, query_tuple, result):
        active_chart = BaseAggregateChart()

        active_chart.stride = 1
        active_chart.min_value = 10.0
        active_chart.data_x_axis = "x"
        self.result = ""

        def reset_chart(datatile_result):
            self.result = datatile_result

        active_chart.reset_chart = reset_chart
        active_chart.source = ColumnDataSource(
            {
                "x": np.array([10.0, 11.0, 12.0, 13.0, 14.0]),
                "y": np.array([1, 1, 1, 1, 1]),
            }
        )
        active_chart.source_backup = pd.DataFrame(
            {
                "x": np.array([10.0, 11.0, 12.0, 13.0, 14.0]),
                "y": np.array([1, 1, 1, 1, 1]),
            }
        )

        datatile = pd.DataFrame(
            {
                0: {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                1: {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0},
                2: {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0},
                3: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0},
                4: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            }
        )

        active_chart.query_chart_by_range(active_chart, query_tuple, datatile)

        assert all(result == self.result)

    @pytest.mark.parametrize(
        "old_indices, new_indices, prev_result,result",
        [
            ([], [0], [0.0, 0.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0, 0.0]),
            (
                [0],
                [0, 1],
                [1.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 1.0, 0.0, 0.0, 0.0],
            ),
            ([0, 1], [], [1.0, 0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0, 1.0]),
            (
                [],
                [0, 1, 2, 3, 4],
                [1.0, 1.0, 1.0, 1.0, 1.0],
                [1.0, 1.0, 1.0, 1.0, 1.0],
            ),
        ],
    )
    def test_query_chart_by_indices(
        self, old_indices, new_indices, prev_result, result
    ):
        active_chart = BaseAggregateChart()
        passive_chart = BaseAggregateChart()

        active_chart.stride = 1
        active_chart.min_value = 0.0
        active_chart.aggregate_fn = "count"
        active_chart.data_points = 5
        passive_chart.stride = 1
        passive_chart.min_value = 2.0
        passive_chart.data_points = 5
        self.result = None

        def f_temp():
            return prev_result

        passive_chart.get_source_y_axis = f_temp

        def reset_chart(datatile_result):
            self.result = datatile_result

        passive_chart.reset_chart = reset_chart
        passive_chart.source = ColumnDataSource(
            {
                "x": np.array([2.0, 3.0, 4.0, 5.0, 6.0]),
                "y": np.array([1, 1, 1, 1, 1]),
            }
        )
        passive_chart.data_x_axis = "x"
        datatile = pd.DataFrame(
            {
                0: {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                1: {0: 0.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0},
                2: {0: 0.0, 1: 0.0, 2: 1.0, 3: 0.0, 4: 0.0},
                3: {0: 0.0, 1: 0.0, 2: 0.0, 3: 1.0, 4: 0.0},
                4: {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 1.0},
            }
        )

        passive_chart.query_chart_by_indices(
            active_chart, old_indices, new_indices, datatile
        )
        assert all(self.result == result)
