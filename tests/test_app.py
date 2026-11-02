"""End-to-end tests that run app.py with Streamlit's built-in test harness."""

from streamlit.testing.v1 import AppTest


def run_app():
    at = AppTest.from_file("../app.py", default_timeout=60)
    at.run()
    return at


def test_app_loads_without_errors():
    at = run_app()
    assert not at.exception, f"App raised: {at.exception}"
    assert "Fitbit Activity Clustering" in at.title[0].value


def test_app_shows_cluster_table():
    at = run_app()
    assert len(at.dataframe) >= 1


def test_predict_button_returns_a_cluster():
    at = run_app()
    at.button[0].click().run()
    assert not at.exception
    assert len(at.success) == 1
    assert "Cluster" in at.success[0].value


def _predict(at, steps, very_active, sedentary):
    """Fill in the form with a profile and submit it."""
    inputs = {ni.label: ni for ni in at.number_input}
    inputs["Total Steps"].set_value(steps)
    inputs["Very Active Minutes"].set_value(very_active)
    inputs["Sedentary Minutes"].set_value(sedentary)
    at.button[0].click().run()
    return " ".join(md.value for md in at.markdown)


def test_very_active_user_is_labelled_highly_active():
    at = run_app()
    text = _predict(at, steps=20000, very_active=120, sedentary=600)
    assert "Highly Active" in text


def test_inactive_user_is_labelled_sedentary():
    at = run_app()
    text = _predict(at, steps=500, very_active=0, sedentary=1300)
    assert "Sedentary Users" in text
