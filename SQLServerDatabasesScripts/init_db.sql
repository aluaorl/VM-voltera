CREATE DATABASE VolterraDB;
GO

USE VolterraDB;
GO

DROP TABLE IF EXISTS UserCalculations;
GO

CREATE TABLE UserCalculations (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    SessionId NVARCHAR(100) NOT NULL,
    KernelExpression NVARCHAR(MAX) NOT NULL,
    RhsExpression NVARCHAR(MAX) NOT NULL,
    XMin FLOAT NOT NULL,
    XMax FLOAT NOT NULL,
    InitialCondition FLOAT DEFAULT 0.0,
    XValuesJson NVARCHAR(MAX),
    PhiValuesJson NVARCHAR(MAX),
    ExecutionTimeMs FLOAT,
    CreatedAt DATETIME DEFAULT GETDATE(),
    IsSuccessful BIT DEFAULT 1
);
GO

DROP TABLE IF EXISTS CryptoArtifacts;
GO

CREATE TABLE CryptoArtifacts (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    SessionId NVARCHAR(100) NOT NULL,
    OperationType NVARCHAR(50) NOT NULL,
    PublicKeyPem NVARCHAR(MAX),
    SignatureHex NVARCHAR(MAX),
    CertificateChainJson NVARCHAR(MAX),
    VerifyResult NVARCHAR(MAX),
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='EquationPresets' and xtype='U')
BEGIN
    CREATE TABLE EquationPresets (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Title NVARCHAR(200) NOT NULL,
        Category NVARCHAR(50) NOT NULL,
        SessionId NVARCHAR(100) NULL,
        KernelExpression NVARCHAR(MAX) NOT NULL,
        RhsExpression NVARCHAR(MAX) NOT NULL,
        XMin FLOAT DEFAULT 0.0,
        XMax FLOAT DEFAULT 1.0,
        StepsCount INT DEFAULT 100,
        InitialCondition FLOAT DEFAULT 0.0,
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

IF NOT EXISTS (SELECT * FROM EquationPresets)
BEGIN
    INSERT INTO EquationPresets (Title, Category, KernelExpression, RhsExpression, XMin, XMax, StepsCount, InitialCondition)
    VALUES 
    ('Простейшее линейное ядро', 'system', 'x * t', 'x', 0.0, 1.0, 100, 0.0),
    ('Ядро с экспонентой', 'system', 'exp(x - t)', '1', 0.0, 1.0, 100, 0.0),
    ('Тригонометрическое уравнение', 'system', 'sin(x * t)', 'cos(x)', 0.0, 3.14, 150, 1.0);
END
GO