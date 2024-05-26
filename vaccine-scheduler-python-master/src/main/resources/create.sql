CREATE TABLE Caregiver (
    username VARCHAR(255) PRIMARY KEY,
    salt BINARY(16),
    hash BINARY(16)
);

CREATE TABLE Patients (
    username VARCHAR(255) PRIMARY KEY,
    salt BINARY(16),
    hash BINARY(16)
);

CREATE TABLE Vaccines (
    Name VARCHAR(255) PRIMARY KEY,
    Doses INT
);

CREATE TABLE Availabilities (
    date DATE,
    username VARCHAR(255) REFERENCES Caregiver
    PRIMARY KEY (date, username),
);

CREATE TABLE Appointments (
    appointment_id INT PRIMARY KEY,
    date DATE,
    cid VARCHAR(255),
    pid VARCHAR(255),
    vaccine_name VARCHAR(255),
    FOREIGN KEY (cid) REFERENCES Caregiver(username),
    FOREIGN KEY (pid) REFERENCES Patients(username),
    FOREIGN KEY (vaccine_name) REFERENCES Vaccines(Name)
);






