INSERT INTO User (id, name, email, pass) VALUES (1, 'Admin User', 'admin@havnhut.com', 'scrypt:32768:8:1$jw4GlsDTtnWOdiIq$4ee675317cc4fab9cf8c9d26b21c15dbfd1249c1fddd2fb665a531544c2c40c77cbf243a9081c2d97fe6c5c21710e23a85ba4ce78ccb9a5a2741325283d3fbbd');
INSERT INTO User (id, name, email, pass) VALUES (2, 'John Doe', 'john@example.com', 'scrypt:32768:8:1$hlp1sujiKWhKgONu$dfc627bd347ee065966fb05c7cd67f52506f1a1f4ea9de8afaf4effbcb14abfe714600f65439cb7bdb6b1183c63142c89ce5aa6dd40b85c61c64142c40026347');
INSERT INTO User (id, name, email, pass) VALUES (3, 'asd', 'asd@f.gh', 'scrypt:32768:8:1$hlp1sujiKWhKgONu$dfc627bd347ee065966fb05c7cd67f52506f1a1f4ea9de8afaf4effbcb14abfe714600f65439cb7bdb6b1183c63142c89ce5aa6dd40b85c61c64142c40026347');
INSERT INTO User (id, name, email, pass) VALUES (4, 'Dr. Sarah Chen', 'sarah.chen@havnhut.com', 'scrypt:32768:8:1$hlp1sujiKWhKgONu$dfc627bd347ee065966fb05c7cd67f52506f1a1f4ea9de8afaf4effbcb14abfe714600f65439cb7bdb6b1183c63142c89ce5aa6dd40b85c61c64142c40026347');
INSERT INTO User (id, name, email, pass) VALUES (5, 'Dr. Michael Torres', 'michael.torres@havnhut.com', 'scrypt:32768:8:1$hlp1sujiKWhKgONu$dfc627bd347ee065966fb05c7cd67f52506f1a1f4ea9de8afaf4effbcb14abfe714600f65439cb7bdb6b1183c63142c89ce5aa6dd40b85c61c64142c40026347');
INSERT INTO User (id, name, email, pass) VALUES (6, 'Dr. Emily Johnson', 'emily.johnson@havnhut.com', 'scrypt:32768:8:1$hlp1sujiKWhKgONu$dfc627bd347ee065966fb05c7cd67f52506f1a1f4ea9de8afaf4effbcb14abfe714600f65439cb7bdb6b1183c63142c89ce5aa6dd40b85c61c64142c40026347');

INSERT INTO Admin (user_id) VALUES (1);

INSERT INTO GeneralUser (user_id) VALUES (2);
INSERT INTO GeneralUser (user_id) VALUES (3);

INSERT INTO Consultant (user_id, full_name, phone_no, address) VALUES (4, 'Dr. Sarah Chen', '01712345001', '123 Pet Care Road, Dhaka');
INSERT INTO Consultant (user_id, full_name, phone_no, address) VALUES (5, 'Dr. Michael Torres', '01712345002', '456 Animal Lane, Dhaka');
INSERT INTO Consultant (user_id, full_name, phone_no, address) VALUES (6, 'Dr. Emily Johnson', '01712345003', '789 Veterinary Street, Dhaka');

INSERT INTO TimeSlot (id, slot) VALUES (1, '10:00 - 10:50');
INSERT INTO TimeSlot (id, slot) VALUES (2, '11:00 - 11:50');
INSERT INTO TimeSlot (id, slot) VALUES (3, '12:00 - 12:50');
INSERT INTO TimeSlot (id, slot) VALUES (4, '13:00 - 13:50');
INSERT INTO TimeSlot (id, slot) VALUES (5, '14:00 - 14:50');
INSERT INTO TimeSlot (id, slot) VALUES (6, '15:00 - 15:50');

INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (1, 'Fluffy', 'Cat', 'Persian', 'White', 3, 'Female', 'Small', 4.5, 'Litter trained', 'A sweet and gentle cat', 'Premium cat food', 'Calm and friendly', 'https://images.pexels.com/photos/35483577/pexels-photo-35483577.jpeg');
INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (2, 'Max', 'Dog', 'Golden Retriever', 'Golden', 5, 'Male', 'Large', 30.0, 'Basic obedience', 'Energetic and playful dog', 'Dog food, treats', 'Very friendly, loves people', 'https://images.pexels.com/photos/38538/dog-golden-retriver-dog-portrait-beauty-38538.jpeg');
INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (5, 'Mittens', 'Cat', 'Tabby', 'Brown', 2, 'Female', 'Medium', 5.0, 'Indoor trained', 'Playful young cat', 'Dry and wet food', 'Playful and curious', 'https://images.pexels.com/photos/35537372/pexels-photo-35537372.jpeg');
INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (6, 'Buddy', 'Dog', 'Beagle', 'Tri-color', 4, 'Male', 'Medium', 12.0, 'Trained', 'Loyal companion', 'Dog food', 'Friendly and energetic', 'https://images.pexels.com/photos/3764318/pexels-photo-3764318.jpeg');
INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (7, 'Luna', 'Cat', 'Siamese', 'Cream', 3, 'Female', 'Small', 4.0, 'Litter trained', 'Elegant and vocal cat', 'Premium cat food', 'Vocal and affectionate', 'https://images.pexels.com/photos/35473655/pexels-photo-35473655.png');
INSERT INTO Animal (id, title, type, breed, color, age, sex, size, weight, training, description, diet, behaviour, img_url) VALUES (8, 'Rocky', 'Dog', 'Bulldog', 'Brindle', 6, 'Male', 'Medium', 25.0, 'Basic trained', 'Gentle giant', 'Specialized dog food', 'Calm and protective', 'https://images.pexels.com/photos/3930940/pexels-photo-3930940.jpeg');

INSERT INTO Post (id, content, img_url, date, time, admin_id) VALUES (1, 'Welcome to Havnhut! We are excited to help you find your perfect pet companion. Check out our available animals and feel free to reach out with any questions.', NULL, 2025-12-15, 10:00:00, 1);
INSERT INTO Post (id, content, img_url, date, time, admin_id) VALUES (2, 'New arrivals this week! We have several adorable cats and dogs looking for loving homes. Visit our shelter or browse online to meet them.', NULL, 2025-12-14, 14:30:00, 1);
INSERT INTO Post (id, content, img_url, date, time, admin_id) VALUES (3, 'Adoption Success Story: Max found his forever home! Thank you to everyone who supports our mission.', NULL, 2025-12-13, 9:15:00, 1);