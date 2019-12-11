-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 11, 2019 at 08:05 AM
-- Server version: 10.4.6-MariaDB
-- PHP Version: 7.3.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `neurahealth_users`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `doctor_id` int(4) NOT NULL,
  `doctor_name` varchar(50) NOT NULL,
  `pass_word` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `hospital_name` varchar(50) NOT NULL,
  `hospital_code` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`doctor_id`, `doctor_name`, `pass_word`, `email`, `hospital_name`, `hospital_code`) VALUES
(1, 'Aelita', 'fairuz123', 'aelita@gmail.com', 'Sehat Hospital', '00'),
(2, 'satu2', '123', 'satu@gmail.com', 'PHC', '123'),
(3, 'Fero', '999', 'gege@gmail.com', 'halo', '456'),
(4, 'kholil', '123', 'kholil@gmail.com', 'MMN', '123_'),
(5, 'momo', '123', 'momo@gmail.com', 'iya', '123'),
(6, 'askara', '234', 'ask@gmail.com', 'RSUD DR Soetomo', '069'),
(7, 'Ali', '222', 'akbar@gmail.com', 'RS UPN Jabar', '007');

-- --------------------------------------------------------

--
-- Table structure for table `neurahealth_patients`
--

CREATE TABLE `neurahealth_patients` (
  `patients_ID` int(11) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `birth_plc` varchar(30) DEFAULT NULL,
  `birth_date` varchar(10) DEFAULT NULL,
  `ktp` varchar(16) DEFAULT NULL,
  `alamat` varchar(50) DEFAULT NULL,
  `gender` char(1) DEFAULT NULL,
  `result` char(1) DEFAULT NULL,
  `byuser` varchar(30) DEFAULT NULL,
  `diseases` varchar(12) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `neurahealth_patients`
--

INSERT INTO `neurahealth_patients` (`patients_ID`, `name`, `birth_plc`, `birth_date`, `ktp`, `alamat`, `gender`, `result`, `byuser`, `diseases`) VALUES
(1, 'Shireen', 'Jombang', '2000-05-05', '3578101023324576', 'Benowo', 'P', 'Y', 'Fero', 'Tumor'),
(3, 'Ikal', 'Jombang', '1999-12-16', '17081010068', 'Benowo', 'L', 'Y', 'Fero', 'Diabetes'),
(4, 'Agus', 'Lamongan', '2000-05-16', '17081010068', 'Jagir', 'P', 'Y', 'Fero', 'Jantung'),
(5, '1', '1', '1', '1', '1', 'L', 'T', 'Fero', 'Tumor'),
(6, 'Askara', 'Surabaya', '1999-10-10', '17081010086', 'Ngagel', 'L', 'Y', 'momo', 'Parkinson'),
(7, 'Amir', 'Magelang', '1999-12-12', '17081010051', 'PacarKeling', 'P', 'T', 'momo', 'Parkinson'),
(8, 'Sunu', 'Sukabumi', '2019-12-20', '17081010045', 'Sidoarjo', 'L', 'T', 'Fero', 'Tumor'),
(9, 'Fajar', 'Tuban', '2019-12-01', '17081010068', 'Benowo', 'L', 'Y', 'askara', 'Malaria'),
(10, 'Rahadi', 'Sisimangaraja', '2019-12-01', '17081010086', 'Benowo', 'L', 'Y', 'askara', 'Jantung'),
(11, 'Amir', 'Magelang', '2019-12-05', '17081010051', 'Blukid', 'P', 'T', 'askara', 'Tumor'),
(12, 'Ciri', 'Madura', '2019-12-19', '170801010001', 'Madura', 'L', 'Y', 'askara', 'Diabetes'),
(13, 'Unus', 'England', '2019-12-07', '17081010068', 'TTT', 'L', 'T', 'askara', 'Parkinson'),
(14, 'Ikal', 'Jombang', '2019-12-04', '17081010068', 'Benowo', 'L', 'Y', 'Ali', 'Malaria'),
(15, 'Fero', 'Surabaya', '2019-12-02', '17081010086', 'Bojonegoro', 'P', 'Y', 'Ali', 'Tumor'),
(16, 'Momo', 'Banyuwangi', '2019-12-03', '17081010099', 'Surabaya', 'P', 'Y', 'Ali', 'Jantung'),
(17, 'Ciri', 'Bondowoso', '2019-12-01', '17081010999', 'Jagir', 'P', 'Y', 'Ali', 'Diabetes'),
(18, 'Askara', 'Jakarta', '2019-03-03', '17081010100', 'Bali', 'L', 'Y', 'Ali', 'Parkinson');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`doctor_id`);

--
-- Indexes for table `neurahealth_patients`
--
ALTER TABLE `neurahealth_patients`
  ADD PRIMARY KEY (`patients_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `doctor_id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `neurahealth_patients`
--
ALTER TABLE `neurahealth_patients`
  MODIFY `patients_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
