# enrollment/charts/leader.py


class LeaderEnrollmentChart:
    """Chart for visualizing leader enrollments across factions or facilities."""

    def __init__(self, title="Leader Enrollments", chart_type="bar"):
        self.title = title
        self.chart_type = chart_type
        self.labels = []  # Factions or Facilities
        self.data = []  # Enrollment counts
        self.colors = []

    def add_data(self, label, data_points, color="rgba(75, 192, 192, 0.2)"):
        """Add data to the chart."""
        self.labels.append(label)
        self.data.append(data_points)
        self.colors.append(color)

    def get_chart_context(self):
        """Return chart data for Chart.js."""
        return {
            "type": self.chart_type,
            "data": {
                "labels": self.labels,
                "datasets": [
                    {
                        "label": self.title,
                        "data": self.data,
                        "backgroundColor": self.colors,
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "borderWidth": 1,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "top"},
                    "title": {"display": True, "text": self.title},
                },
            },
        }
