import subprocess
import os

KEYS_DIR = "/tmp/openssl_keys"

def ensure_keys_dir():
    os.makedirs(KEYS_DIR, exist_ok=True)

def run_openssl(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"OpenSSL error ({cmd}): {res.stderr}")
    return res.stdout.strip()

def generate_and_verify_ec_signature(payload_text: str):
    """1. Генерация EC secp521r1 ключей, подпись SHA3-512 и верификация"""
    ensure_keys_dir()
    priv = os.path.join(KEYS_DIR, "ec_keypair.pem")
    pub = os.path.join(KEYS_DIR, "ec_public_key.pem")
    data_file = os.path.join(KEYS_DIR, "payload.txt")
    sig_file = os.path.join(KEYS_DIR, "payload.sig")

    with open(data_file, "w", encoding="utf-8") as f:
        f.write(payload_text)

    # Генерация приватного и публичного ключей
    run_openssl(f"openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:secp521r1 -out {priv}")
    run_openssl(f"openssl pkey -in {priv} -pubout -out {pub}")

    # Создание подписи и проверка
    run_openssl(f"openssl pkeyutl -sign -digest sha3-512 -inkey {priv} -in {data_file} -rawin -out {sig_file}")
    verify_out = run_openssl(f"openssl pkeyutl -verify -digest sha3-512 -inkey {priv} -in {data_file} -rawin -sigfile {sig_file}")

    with open(pub, "r") as f:
        pub_pem = f.read()
    with open(sig_file, "rb") as f:
        sig_hex = f.read().hex()

    return {
        "public_key_pem": pub_pem,
        "signature_hex": sig_hex,
        "verify_status": verify_out  
    }

def generate_and_verify_cert_chain():
    """2. Генерация Root -> Intermediate -> Leaf сертификатов (ED448) и проверка цепочки"""
    ensure_keys_dir()
    r_key, r_csr, r_crt = [os.path.join(KEYS_DIR, f"root_{x}.pem") for x in ("keypair", "csr", "cert")]
    i_key, i_csr, i_crt = [os.path.join(KEYS_DIR, f"intermediate_{x}.pem") for x in ("keypair", "csr", "cert")]
    l_key, l_csr, l_crt = [os.path.join(KEYS_DIR, f"leaf_{x}.pem") for x in ("keypair", "csr", "cert")]

    # Root CA
    run_openssl(f"openssl genpkey -algorithm ED448 -out {r_key}")
    run_openssl(f'openssl req -new -subj "/CN=Root CA" -addext "basicConstraints=critical,CA:TRUE" -key {r_key} -out {r_csr}')
    run_openssl(f"openssl x509 -req -in {r_csr} -copy_extensions copyall -key {r_key} -days 3650 -out {r_crt}")

    # Intermediate CA
    run_openssl(f"openssl genpkey -algorithm ED448 -out {i_key}")
    run_openssl(f'openssl req -new -subj "/CN=Root Intermediate CA" -addext "basicConstraints=critical,CA:TRUE" -key {i_key} -out {i_csr}')
    run_openssl(f"openssl x509 -req -in {i_csr} -copy_extensions copyall -CA {r_crt} -CAkey {r_key} -days 3650 -out {i_crt}")

    # Leaf Certificate
    run_openssl(f"openssl genpkey -algorithm ED448 -out {l_key}")
    run_openssl(f'openssl req -new -subj "/CN=Leaf" -addext "basicConstraints=critical,CA:TRUE" -key {l_key} -out {l_csr}')
    run_openssl(f"openssl x509 -req -in {l_csr} -copy_extensions copyall -CA {i_crt} -CAkey {i_key} -days 3650 -out {l_crt}")

    # Валидация цепочки
    chain_verify = run_openssl(f"openssl verify -verbose -show_chain -trusted {r_crt} -untrusted {i_crt} {l_crt}")

    certs = {}
    for name, path in [("root", r_crt), ("intermediate", i_crt), ("leaf", l_crt)]:
        with open(path, "r") as f:
            certs[name] = f.read()

    return {
        "certificates": certs,
        "chain_verify": chain_verify
    }