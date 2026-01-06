CREATE TABLE User (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    pass VARCHAR(255) NOT NULL
);

CREATE TABLE GeneralUser (
    user_id INT PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Admin (
    user_id INT PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Consultant (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    phone_no VARCHAR(20),
    address VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Adopter (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(255),
    address VARCHAR(255),
    phone_no VARCHAR(20),
    marital_status VARCHAR(50),
    job VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE Animal (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    type VARCHAR(50),
    breed VARCHAR(100),
    color VARCHAR(50),
    age INT,
    sex VARCHAR(10),
    size VARCHAR(20),
    weight FLOAT,
    training VARCHAR(255),
    description TEXT,
    diet TEXT,
    behaviour TEXT,
    img_url VARCHAR(255)
);

CREATE TABLE Adopt (
    animal_id INT,
    adopter_id INT,
    adoption_date DATE,
    approved BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (animal_id, adopter_id),
    FOREIGN KEY (animal_id) REFERENCES Animal(id) ON DELETE CASCADE,
    FOREIGN KEY (adopter_id) REFERENCES Adopter(user_id) ON DELETE CASCADE
);

CREATE TABLE Donation (
    id INT PRIMARY KEY,
    amount DECIMAL(10, 2),
    method VARCHAR(50),
    trx_id VARCHAR(100),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE SET NULL
);

CREATE TABLE Notification (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE TimeSlot (
    id INT PRIMARY KEY,
    slot VARCHAR(50)
);

CREATE TABLE Appointment (
    adopter_id INT,
    consultant_id INT,
    timeslot_id INT,
    PRIMARY KEY (adopter_id, consultant_id, timeslot_id),
    FOREIGN KEY (adopter_id) REFERENCES Adopter(user_id) ON DELETE CASCADE,
    FOREIGN KEY (consultant_id) REFERENCES Consultant(user_id) ON DELETE CASCADE,
    FOREIGN KEY (timeslot_id) REFERENCES TimeSlot(id) ON DELETE CASCADE
);

CREATE TABLE Blog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    img_url VARCHAR(255),
    date DATE,
    time TIME,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE SET NULL
);



CREATE TABLE Blog_Comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT,
    date DATE,
    time TIME,
    user_id INT,
    blog_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (blog_id) REFERENCES Blog(id) ON DELETE CASCADE
);


CREATE TABLE Blog_Like (
    user_id INT,
    blog_id INT,
    date DATE,
    time TIME,
    PRIMARY KEY (user_id, blog_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (blog_id) REFERENCES Blog(id) ON DELETE CASCADE
);

CREATE TABLE Post (
    id INT PRIMARY KEY,
    content TEXT,
    img_url VARCHAR(255),
    date DATE,
    time TIME,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES Admin(user_id) ON DELETE SET NULL
);

CREATE TABLE Post_Comment (
    id INT PRIMARY KEY,
    content TEXT,
    date DATE,
    time TIME,
    user_id INT,
    post_id INT,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES Post(id) ON DELETE CASCADE
);

CREATE TABLE Post_Like (
    user_id INT,
    post_id INT,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES Post(id) ON DELETE CASCADE
);