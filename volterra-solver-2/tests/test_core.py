import os
import sys
import numpy as np

# Добавляем корневую директорию приложения (volterra-solver-2) в sys.path
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from expression_parser import validate_expression_detailed, parse_user_input
from calculation_engine import solve_volterra_RK4, create_function_from_string
from crypto_manager import generate_and_verify_ec_signature, generate_and_verify_cert_chain


def test_expression_validation():
    ok_k, _ = validate_expression_detailed("x + t", ["x", "t"])
    bad_k, _ = validate_expression_detailed("x + z", ["x", "t"])
    ok_f, _ = validate_expression_detailed("sin(x) + 1", ["x"])
    parsed = parse_user_input("2*x + sin(t)", ["x", "t"])

    assert ok_k is True
    assert bad_k is False
    assert ok_f is True
    assert "np.sin" in parsed


def test_volterra_solver_rk4():
    # Простое тестовое уравнение: phi'(x) = 1, phi(0) = 0 -> phi(x) = x
    K = create_function_from_string("0", ["x", "t"])
    f = create_function_from_string("1", ["x"])
    x = np.linspace(0, 1, 101)
    h = x[1] - x[0]
    phi, _ = solve_volterra_RK4(x, h, K, f, 0.0)
    assert np.allclose(phi, x, atol=1e-4)


def test_openssl_crypto():
    sig_res = generate_and_verify_ec_signature("test-payload")
    assert "Successfully" in sig_res["verify_status"]

    cert_res = generate_and_verify_cert_chain()
    assert "OK" in cert_res["chain_verify"]