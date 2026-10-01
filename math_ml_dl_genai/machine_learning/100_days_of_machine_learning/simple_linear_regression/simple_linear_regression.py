from collections.abc import Iterable
from math import isclose


class SimpleLinearRegression:
	"""Ordinary least-squares regression for one feature."""

	def __init__(self) -> None:
		self.slope: float | None = None
		self.intercept: float | None = None

	def fit(self, x: Iterable[float], y: Iterable[float]) -> "SimpleLinearRegression":
		"""Fit ``y = slope * x + intercept`` and return this model."""
		features = [float(value) for value in x]
		targets = [float(value) for value in y]

		if not features or len(features) != len(targets):
			raise ValueError("x and y must contain the same non-zero number of values")

		mean_x = sum(features) / len(features)
		mean_y = sum(targets) / len(targets)
		centered_x = [value - mean_x for value in features]
		denominator = sum(value * value for value in centered_x)

		if isclose(denominator, 0.0):
			raise ValueError("x must contain at least two distinct values")

		numerator = sum(
			x_value * (y_value - mean_y)
			for x_value, y_value in zip(centered_x, targets)
		)
		self.slope = numerator / denominator
		self.intercept = mean_y - self.slope * mean_x
		return self

	def predict(self, x: Iterable[float]) -> list[float]:
		"""Predict target values for an iterable of feature values."""
		if self.slope is None or self.intercept is None:
			raise ValueError("fit the model before making predictions")

		return [self.slope * float(value) + self.intercept for value in x]

	def score(self, x: Iterable[float], y: Iterable[float]) -> float:
		"""Return the coefficient of determination, R-squared."""
		targets = [float(value) for value in y]
		if not targets:
			raise ValueError("y must contain at least one value")

		predictions = self.predict(x)
		if len(predictions) != len(targets):
			raise ValueError("x and y must contain the same number of values")

		mean_y = sum(targets) / len(targets)
		total_sum_of_squares = sum((value - mean_y) ** 2 for value in targets)
		if isclose(total_sum_of_squares, 0.0):
			return 1.0 if all(isclose(prediction, targets[0]) for prediction in predictions) else 0.0

		residual_sum_of_squares = sum(
			(target - prediction) ** 2
			for target, prediction in zip(targets, predictions)
		)
		return 1.0 - residual_sum_of_squares / total_sum_of_squares


if __name__ == "__main__":
	model = SimpleLinearRegression().fit([1, 2, 3, 4], [3, 5, 7, 9])
	print(f"slope={model.slope}, intercept={model.intercept}")
	print(f"predictions={model.predict([5, 6])}")
	print(f"r_squared={model.score([1, 2, 3, 4], [3, 5, 7, 9])}")
