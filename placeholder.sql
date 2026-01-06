INSERT INTO User (id, name, email, pass) 
VALUES (1, 'Admin User', 'admin@havnhut.com', 'scrypt:32768:8:1$PYxqJ8ZKLQGnXE0v$8f1e3a5c7b2d4f6e8a0c2e4f6a8b0d2e4f6a8c0e2f4a6c8e0f2a4c6e8f0a2c4e6f8a0c2e4f6a8c0e2f4a6c8e0f2a4c6e8f0a2c4e6f8a0c2e4f6a8c0e2f4a6c8e');

INSERT INTO Admin (user_id) VALUES (1);

INSERT INTO User (id, name, email, pass) 
VALUES (2, 'John Doe', 'john@example.com', 'scrypt:32768:8:1$PYxqJ8ZKLQGnXE0v$8f1e3a5c7b2d4f6e8a0c2e4f6a8b0d2e4f6a8c0e2f4a6c8e0f2a4c6e8f0a2c4e6f8a0c2e4f6a8c0e2f4a6c8e0f2a4c6e8f0a2c4e6f8a0c2e4f6a8c0e2f4a6c8e');
INSERT INTO GeneralUser (user_id) VALUES (2);

INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url)
VALUES 
(1, 'Fluffy', 'Cat', 'Persian', 'White', 3, 'Female', 'Small', 4.5, 'Litter trained', 'A sweet and gentle cat', 'Premium cat food', 'Calm and friendly', 'https://placekitten.com/300/300'),
(2, 'Max', 'Dog', 'Golden Retriever', 'Golden', 5, 'Male', 'Large', 30.0, 'Basic obedience', 'Energetic and playful dog', 'Dog food, treats', 'Very friendly, loves people', 'https://placedog.net/300/300'),
(3, 'Tweety', 'Bird', 'Canary', 'Yellow', 2, 'Male', 'Small', 0.05, 'None', 'Beautiful singing bird', 'Seeds and fruits', 'Active and vocal', NULL),
(4, 'Nemo', 'Fish', 'Clownfish', 'Orange', 1, 'Male', 'Small', 0.02, NULL, 'Colorful tropical fish', 'Fish flakes', 'Peaceful', NULL),
(5, 'Mittens', 'Cat', 'Tabby', 'Brown', 2, 'Female', 'Medium', 5.0, 'Indoor trained', 'Playful young cat', 'Dry and wet food', 'Playful and curious', 'https://placekitten.com/301/301'),
(6, 'Buddy', 'Dog', 'Beagle', 'Tri-color', 4, 'Male', 'Medium', 12.0, 'Trained', 'Loyal companion', 'Dog food', 'Friendly and energetic', 'https://placedog.net/301/301'),
(7, 'Luna', 'Cat', 'Siamese', 'Cream', 3, 'Female', 'Small', 4.0, 'Litter trained', 'Elegant and vocal cat', 'Premium cat food', 'Vocal and affectionate', 'https://placekitten.com/302/302'),
(8, 'Rocky', 'Dog', 'Bulldog', 'Brindle', 6, 'Male', 'Medium', 25.0, 'Basic trained', 'Gentle giant', 'Specialized dog food', 'Calm and protective', 'https://placedog.net/302/302');


INSERT INTO Post (id, content, img_url, date, time, admin_id)
VALUES 
(1, 'Welcome to Havnhut! We are excited to help you find your perfect pet companion. Check out our available animals and feel free to reach out with any questions.', NULL, '2025-12-15', '10:00:00', 1),
(2, 'New arrivals this week! We have several adorable cats and dogs looking for loving homes. Visit our shelter or browse online to meet them.', NULL, '2025-12-14', '14:30:00', 1),
(3, 'Adoption Success Story: Max found his forever home! Thank you to everyone who supports our mission.', NULL, '2025-12-13', '09:15:00', 1);

