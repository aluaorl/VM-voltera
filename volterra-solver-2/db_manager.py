import os
import json
import pyodbc
import numpy as np


def get_db_connection():
    server = os.environ.get("DB_HOST", "localhost")
    database = os.environ.get("DB_NAME", "VolterraDB")
    username = os.environ.get("DB_USER", "sa")
    password = os.environ.get("DB_PASSWORD", "YourStrongPassword123!")
    port = os.environ.get("DB_PORT", "1433")

    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def save_calculation_to_db(session_id, kernel, rhs, x_min, x_max, initial_condition, computation_time, x_arr, phi_arr):
    """Сохранение расчета в таблицу UserCalculations"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO UserCalculations 
        (SessionId, KernelExpression, RhsExpression, XMin, XMax, InitialCondition, 
         XValuesJson, PhiValuesJson, ExecutionTimeMs, IsSuccessful)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """
    cursor.execute(query, (
        str(session_id),
        str(kernel),
        str(rhs),
        float(x_min if x_min is not None else 0.0),
        float(x_max if x_max is not None else 1.0),
        float(initial_condition),
        json.dumps(x_arr.tolist() if isinstance(x_arr, np.ndarray) else x_arr),
        json.dumps(phi_arr.tolist() if isinstance(phi_arr, np.ndarray) else phi_arr),
        float(computation_time * 1000)  # в миллисекундах
    ))
    conn.commit()
    cursor.close()
    conn.close()
    print("Успешно сохранено в БД!")


def get_user_history_from_db(session_id=None):
    """Загрузка последних 20 записей из истории"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT TOP 20
                Id, 
                CONVERT(VARCHAR(8), CreatedAt, 108) as timestamp_str, 
                CONVERT(VARCHAR(10), CreatedAt, 104) as date_str,
                KernelExpression, 
                RhsExpression, 
                InitialCondition, 
                ISNULL(ExecutionTimeMs, 0) / 1000.0
            FROM UserCalculations 
            ORDER BY CreatedAt DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        history_list = []
        for row in rows:
            history_list.append({
                'id': str(row[0]),
                'timestamp': row[1],
                'date': row[2],
                'kernel': row[3],
                'rhs': row[4],
                'initial_condition': row[5],
                'computation_time': row[6]
            })
        cursor.close()
        conn.close()
        return history_list
    except Exception as e:
        print(f"Ошибка чтения истории из БД: {e}")
        return []


def delete_calculation_from_db(record_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM UserCalculations WHERE Id = ?", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка удаления из БД: {e}")


def clear_user_history_in_db(session_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM UserCalculations")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка очистки истории в БД: {e}")


def save_crypto_artifact_to_db(session_id, operation_type, pub_key=None, signature=None, certs_dict=None, verify_result=None):
    """Запись результатов OpenSSL (ключей, подписей, сертификатов) в БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO CryptoArtifacts 
        (SessionId, OperationType, PublicKeyPem, SignatureHex, CertificateChainJson, VerifyResult)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        str(session_id),
        str(operation_type),
        str(pub_key) if pub_key else None,
        str(signature) if signature else None,
        json.dumps(certs_dict) if certs_dict else None,
        str(verify_result) if verify_result else None
    ))
    conn.commit()
    cursor.close()
    conn.close()


def get_latest_crypto_artifacts():
    """Считывание последних криптографических записей из БД"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 5 Id, SessionId, OperationType, VerifyResult, CreatedAt 
            FROM CryptoArtifacts 
            ORDER BY CreatedAt DESC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [
            {
                "id": r[0],
                "session_id": r[1],
                "operation_type": r[2],
                "verify_result": r[3],
                "created_at": str(r[4])
            }
            for r in rows
        ]
    except Exception as e:
        print(f"Ошибка чтения криптоартефактов из БД: {e}")
        return []