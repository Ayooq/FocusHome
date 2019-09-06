-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Хост: localhost:3306
-- Время создания: Сен 06 2019 г., 11:51
-- Версия сервера: 5.7.27-0ubuntu0.18.04.1
-- Версия PHP: 7.2.19-0ubuntu0.18.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `focus`
--

-- --------------------------------------------------------

--
-- Структура таблицы `app_menu`
--

CREATE TABLE `app_menu` (
  `id` int(11) NOT NULL,
  `parent` int(11) DEFAULT NULL COMMENT 'ID родителя для многоуровневого меню',
  `title` varchar(100) DEFAULT NULL COMMENT 'название пункта',
  `href` varchar(100) DEFAULT NULL COMMENT 'ссылка',
  `icon` varchar(100) DEFAULT NULL COMMENT 'иконка',
  `perm` varchar(100) DEFAULT NULL COMMENT 'разрешение на показ',
  `is_active` tinyint(4) DEFAULT '1' COMMENT 'показывать?'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Главное меню приложения';

--
-- Дамп данных таблицы `app_menu`
--

INSERT INTO `app_menu` (`id`, `parent`, `title`, `href`, `icon`, `perm`, `is_active`) VALUES
(1, NULL, 'Клиенты', '/clients/', 'c-blue-500 ti-home', 'app.clients.index', 1),
(2, NULL, 'Оборудование', '/devices/', 'c-brown-500 ti-email', 'app.devices.index', 1),
(3, NULL, 'Пользователи', '/users/', 'c-blue-500 ti-share', 'app.users.index', 1),
(4, NULL, 'Мониторинг', '/monitoring/', 'c-orange-500 ti-layout-list-thumb', 'app.monitoring.devices', 1);

-- --------------------------------------------------------

--
-- Структура таблицы `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `code` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `auth_group`
--

INSERT INTO `auth_group` (`id`, `name`, `code`) VALUES
(1, 'Управление', 'management'),
(2, 'Клиенты', 'clients');

-- --------------------------------------------------------

--
-- Структура таблицы `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `auth_group_permissions`
--

INSERT INTO `auth_group_permissions` (`id`, `group_id`, `permission_id`) VALUES
(21, 2, 57),
(22, 2, 58),
(23, 2, 59),
(24, 2, 60),
(25, 2, 61);

-- --------------------------------------------------------

--
-- Структура таблицы `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(37, 'Can add profiles', 10, 'add_profiles'),
(38, 'Can change profiles', 10, 'change_profiles'),
(39, 'Can delete profiles', 10, 'delete_profiles'),
(40, 'Can view profiles', 10, 'view_profiles'),
(41, 'Can add roles', 11, 'add_roles'),
(42, 'Can change roles', 11, 'change_roles'),
(43, 'Can delete roles', 11, 'delete_roles'),
(44, 'Can view roles', 11, 'view_roles'),
(45, 'Can add group', 12, 'add_group'),
(46, 'Can change group', 12, 'change_group'),
(47, 'Can delete group', 12, 'delete_group'),
(48, 'Can view group', 12, 'view_group'),
(57, 'Пользователи. Просмотр списка', 10, 'users_list'),
(58, 'Пользователи. Просмотр информации', 10, 'users_show'),
(59, 'Пользователи. Редактирование', 10, 'users_edit'),
(60, 'Пользователи. Добавление', 10, 'users_add'),
(61, 'Пользователи. Изменение прав доступа', 10, 'users_perm'),
(67, 'Can add settings', 14, 'add_settings'),
(68, 'Can change settings', 14, 'change_settings'),
(69, 'Can delete settings', 14, 'delete_settings'),
(70, 'Can view settings', 14, 'view_settings'),
(71, 'Can add groups', 15, 'add_groups'),
(72, 'Can change groups', 15, 'change_groups'),
(73, 'Can delete groups', 15, 'delete_groups'),
(74, 'Can view groups', 15, 'view_groups'),
(75, 'Can add types', 16, 'add_types'),
(76, 'Can change types', 16, 'change_types'),
(77, 'Can delete types', 16, 'delete_types'),
(78, 'Can view types', 16, 'view_types'),
(99, 'Can add group', 22, 'add_group'),
(100, 'Can change group', 22, 'change_group'),
(101, 'Can delete group', 22, 'delete_group'),
(102, 'Can view group', 22, 'view_group'),
(103, 'Can add datatype', 23, 'add_datatype'),
(104, 'Can change datatype', 23, 'change_datatype'),
(105, 'Can delete datatype', 23, 'delete_datatype'),
(106, 'Can view datatype', 23, 'view_datatype'),
(107, 'Can add configuration', 24, 'add_configuration'),
(108, 'Can change configuration', 24, 'change_configuration'),
(109, 'Can delete configuration', 24, 'delete_configuration'),
(110, 'Can view configuration', 24, 'view_configuration'),
(111, 'Can add client', 25, 'add_client'),
(112, 'Can change client', 25, 'change_client'),
(113, 'Can delete client', 25, 'delete_client'),
(114, 'Can view client', 25, 'view_client'),
(115, 'Can add device', 26, 'add_device'),
(116, 'Can change device', 26, 'change_device'),
(117, 'Can delete device', 26, 'delete_device'),
(118, 'Can view device', 26, 'view_device'),
(119, 'Can add config', 27, 'add_config'),
(120, 'Can change config', 27, 'change_config'),
(121, 'Can delete config', 27, 'delete_config'),
(122, 'Can view config', 27, 'view_config'),
(123, 'Can add monitor', 28, 'add_monitor'),
(124, 'Can change monitor', 28, 'change_monitor'),
(125, 'Can delete monitor', 28, 'delete_monitor'),
(126, 'Can view monitor', 28, 'view_monitor'),
(127, 'Can add profile', 29, 'add_profile'),
(128, 'Can change profile', 29, 'change_profile'),
(129, 'Can delete profile', 29, 'delete_profile'),
(130, 'Can view profile', 29, 'view_profile'),
(131, 'Can add role', 30, 'add_role'),
(132, 'Can change role', 30, 'change_role'),
(133, 'Can delete role', 30, 'delete_role'),
(134, 'Can view role', 30, 'view_role'),
(135, 'Can add family', 31, 'add_family'),
(136, 'Can change family', 31, 'change_family'),
(137, 'Can delete family', 31, 'delete_family'),
(138, 'Can view family', 31, 'view_family'),
(139, 'Can add unit', 32, 'add_unit'),
(140, 'Can change unit', 32, 'change_unit'),
(141, 'Can delete unit', 32, 'delete_unit'),
(142, 'Can view unit', 32, 'view_unit'),
(143, 'Can add status', 33, 'add_status'),
(144, 'Can change status', 33, 'change_status'),
(145, 'Can delete status', 33, 'delete_status'),
(146, 'Can view status', 33, 'view_status'),
(147, 'Can add event', 34, 'add_event'),
(148, 'Can change event', 34, 'change_event'),
(149, 'Can delete event', 34, 'delete_event'),
(150, 'Can view event', 34, 'view_event'),
(151, 'Can add message', 35, 'add_message'),
(152, 'Can change message', 35, 'change_message'),
(153, 'Can delete message', 35, 'delete_message'),
(154, 'Can view message', 35, 'view_message'),
(155, 'Получение списка всех клиентов', 37, 'app.clients.index'),
(156, 'Создание клиента', 37, 'app.clients.create'),
(157, 'Редактирование клиента', 37, 'app.clients.update'),
(158, 'Просмотр клиента', 37, 'app.clients.show'),
(159, 'Получение списка всех устройств', 38, 'app.devices.index'),
(160, 'Создание устройства', 38, 'app.devices.create'),
(161, 'Редактирование устройства', 38, 'app.devices.update'),
(162, 'Просмотр устройства', 38, 'app.devices.show'),
(163, 'Перезагрузка устройства', 38, 'app.devices.reboot'),
(164, 'Смена клиента устройства', 38, 'app.devices.client.change'),
(165, 'Настройка snmp оборудования', 38, 'app.devices.snmp'),
(166, 'Получение списка всех пользователей', 39, 'app.users.index'),
(167, 'Создание пользователя', 39, 'app.users.create'),
(168, 'Редактирование пользователя', 39, 'app.users.update'),
(169, 'Просмотр пользователя', 39, 'app.users.show'),
(170, 'Редактирование прав пользователя', 39, 'app.users.perm'),
(171, 'Мониторинг', 40, 'app.monitoring.devices');

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `phone` varchar(255) DEFAULT NULL,
  `client_id` int(11) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `phone`, `client_id`, `role_id`) VALUES
(1, 'pbkdf2_sha256$150000$4jrT9yYBAZEy$uydjJm1aEmbz7THV/NGtTJ0h3mNEQJ+dGTBxriBPMv4=', '2019-09-06 03:39:44.511711', 1, 'maksim_serg@mail.ru', 'Имя', 'Фамилия', 'maksim_serg@mail.ru', 1, 1, '2019-07-01 06:46:31.844294', '8-800-555-35-35', 4, 1),
(4, 'pbkdf2_sha256$150000$CVJltjlLwWzN$NcYCLLlS7uVjLIDIzdrjS1NewcK4vgasGmvKUWcMaB8=', '2019-08-26 03:25:08.762799', 1, 'inc12@yandex.ru', 'Влад', 'Плисов', 'inc12@yandex.ru', 1, 1, '2019-07-17 03:23:24.964646', '8-800-555-35-35', 4, 1);

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `auth_user_user_permissions`
--

INSERT INTO `auth_user_user_permissions` (`id`, `user_id`, `permission_id`) VALUES
(66, 1, 155),
(69, 1, 156),
(68, 1, 157),
(67, 1, 158),
(178, 1, 159),
(182, 1, 160),
(180, 1, 161),
(179, 1, 162),
(177, 1, 163),
(181, 1, 164),
(176, 1, 165),
(54, 1, 166),
(55, 1, 167),
(61, 1, 168),
(57, 1, 169),
(58, 1, 170),
(143, 1, 171),
(134, 4, 159),
(138, 4, 160),
(136, 4, 161),
(135, 4, 162),
(133, 4, 163),
(137, 4, 164),
(132, 4, 165);

-- --------------------------------------------------------

--
-- Структура таблицы `broker_dispatcher_log`
--

CREATE TABLE `broker_dispatcher_log` (
  `id` int(11) NOT NULL,
  `created` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `topic` varchar(255) DEFAULT NULL,
  `payload` text,
  `source` varchar(100) DEFAULT NULL,
  `result_code` tinyint(4) DEFAULT NULL,
  `result_message` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `broker_dispatcher_log`
--

INSERT INTO `broker_dispatcher_log` (`id`, `created`, `user_id`, `device_id`, `topic`, `payload`, `source`, `result_code`, `result_message`) VALUES
(15, '2019-09-05 13:30:23', 1, 1, 'FP-1/cmd/cnt3', '1', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f7ab43c5b00>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(16, '2019-09-05 13:30:25', 1, 1, 'FP-1/cmd/cnt2', '0', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f7ab4432160>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(17, '2019-09-05 13:31:41', 1, 2, 'FP-2/cmd/routine/create', '{\n    \"device_id\": \"2\",\n    \"routine_id\": 16,\n    \"routine_name\": \"удалю\",\n    \"routine_comment\": \"\",\n    \"instruction\": {\n        \"routine\": {\n            \"conditions\": [\n                {\n                    \"unit\": \"in1\",\n                    \"compare\": \"eq\",\n                    \"value\": \"1\"\n                }\n            ],\n            \"actions\": [\n                {\n                    \"action\": \"setValue\",\n                    \"unit\": \"out1\",\n                    \"value\": \"1\"\n                }\n            ]\n        }\n    },\n    \"user_id\": 1\n}', 'django dispatcher', 1, NULL),
(18, '2019-09-05 13:31:53', 1, 2, 'FP-2/cmd/routine/update', '{\n    \"device_id\": \"2\",\n    \"routine_id\": 16,\n    \"routine_name\": \"удалю\",\n    \"routine_comment\": \"\",\n    \"instruction\": {\n        \"routine\": {\n            \"conditions\": [\n                {\n                    \"unit\": \"in1\",\n                    \"compare\": \"eq\",\n                    \"value\": \"1\"\n                }\n            ],\n            \"actions\": [\n                {\n                    \"action\": \"setValue\",\n                    \"unit\": \"out1\",\n                    \"value\": \"1\"\n                },\n                {\n                    \"action\": \"setValue\",\n                    \"unit\": \"out3\",\n                    \"value\": \"0\"\n                }\n            ]\n        }\n    },\n    \"user_id\": 1\n}', 'django dispatcher', 1, NULL),
(19, '2019-09-05 13:31:56', 1, 2, 'FP-2/cmd/routine/remove', '{\n    \"device_id\": \"2\",\n    \"routine_id\": 16,\n    \"user_id\": 1\n}', 'django dispatcher', 1, NULL),
(20, '2019-09-05 13:38:27', 1, 1, 'FP-1/snmp/watch/add', '{\n    \"OID\": \".1.3.6.1.4.1.191.39.13.2.1.1.0\",\n    \"interval\": 1440\n}', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f539c60b710>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(21, '2019-09-05 13:39:10', 1, 1, 'FP-1/snmp/watch/remove', '{\n    \"OID\": \".1.3.6.1.4.1.191.39.13.2.1.1.0\"\n}', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f23041ac4a8>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(22, '2019-09-05 13:49:23', 1, 1, 'FP-1/cmd/cnt3', '1', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7fb2a156d748>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(23, '2019-09-05 14:01:49', 1, 1, 'FP-1/snmp/oid/get', '{\n    \"OID\": \".1.3.6.1.4.1.191.1.33.3.1.1.8.30\"\n}', 'django dispatcher', 0, 'HTTPConnectionPool(host=\'127.0.0.1\', port=3000): Max retries exceeded with url: /send_message_to_device (Caused by NewConnectionError(\'<urllib3.connection.HTTPConnection object at 0x7f0b0f6dce10>: Failed to establish a new connection: [Errno 111] Connection refused\',))'),
(27, '2019-09-05 14:08:18', 1, 1, 'FP-1/snmp/get', '\"\"', 'django dispatcher', 1, NULL),
(28, '2019-09-05 14:38:36', 1, 1, 'FP-1/snmp/watch/remove', '{\n    \"OID\": \".1.3.6.1.2.1.1.1.0\"\n}', 'django dispatcher', 1, NULL),
(31, '2019-09-06 10:10:46', NULL, 1, 'FP-1/report/self', '[\"2019-08-27 10:30:37.912656\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(32, '2019-09-06 10:13:09', NULL, NULL, 'FP-1sd/report/self', '[\"2019-08-27 10:30:37.912656\", \"status\", \"offline\"]', 'FP-1sd', 0, 'Неудалось определить оборудование'),
(33, '2019-09-06 10:29:03', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"status\"]', 'FP-2', 1, NULL),
(34, '2019-09-06 10:29:03', NULL, 1, 'FP-1/report/self', '[\"2019-09-04 16:55:56.229875\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(35, '2019-09-06 10:29:12', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"status\"]', 'FP-2', 1, NULL),
(36, '2019-09-06 10:29:12', NULL, 1, 'FP-1/report/self', '[\"2019-09-04 16:55:56.229875\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(37, '2019-09-06 10:29:23', NULL, 1, 'FP-1/report/self', '[\"2019-09-04 16:55:56.229875\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(38, '2019-09-06 10:29:23', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"status\"]', 'FP-2', 1, NULL),
(39, '2019-09-06 10:31:49', NULL, 1, 'FP-1/report/self', '[\"2019-09-05 19:40:57.540818\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(40, '2019-09-06 10:32:06', NULL, 1, 'FP-1/report/self', '[\"2019-09-05 19:40:54.367905\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(41, '2019-09-06 10:32:10', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:10.768270\", \"status\", \"status\"]', 'FP-1', 1, NULL),
(42, '2019-09-06 10:33:28', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(43, '2019-09-06 10:33:28', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:10.768270\", \"status\", \"online\"]', 'FP-1', 1, NULL),
(44, '2019-09-06 10:35:09', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:09.083128\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(45, '2019-09-06 10:35:09', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:09.291346\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(46, '2019-09-06 10:35:09', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:09.414354\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(47, '2019-09-06 10:35:09', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:09.689078\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(48, '2019-09-06 10:35:10', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:10.211893\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(49, '2019-09-06 10:35:10', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:10.378549\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(50, '2019-09-06 10:35:10', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:10.517673\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(51, '2019-09-06 10:35:11', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:11.120637\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(52, '2019-09-06 10:35:11', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:11.283617\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(53, '2019-09-06 10:35:12', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:11.726712\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(54, '2019-09-06 10:35:12', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:11.926321\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(55, '2019-09-06 10:35:12', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:12.388838\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(56, '2019-09-06 10:35:12', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:12.474980\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(57, '2019-09-06 10:35:15', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:15.789181\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(58, '2019-09-06 10:35:16', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:15.896970\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(59, '2019-09-06 10:35:16', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:16.811200\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(60, '2019-09-06 10:35:17', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:17.542294\", \"event\", \"1\"]', 'FP-1', 1, NULL),
(61, '2019-09-06 10:35:19', NULL, 1, 'FP-1/report/in3', '[\"2019-09-06 13:35:19.003334\", \"event\", \"0\"]', 'FP-1', 1, NULL),
(62, '2019-09-06 10:37:37', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(63, '2019-09-06 10:37:37', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:10.768270\", \"status\", \"online\"]', 'FP-1', 1, NULL),
(64, '2019-09-06 10:37:49', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:10.768270\", \"status\", \"online\"]', 'FP-1', 1, NULL),
(65, '2019-09-06 10:37:49', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(66, '2019-09-06 10:39:49', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(67, '2019-09-06 10:39:50', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:39:50.226686\", \"status\", \"online\"]', 'FP-1', 1, NULL),
(68, '2019-09-06 10:39:50', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:39:48.986976\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(69, '2019-09-06 10:39:50', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:39:49.056725\", \"error\", \"1\"]', 'FP-1', 1, NULL),
(70, '2019-09-06 11:10:05', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(71, '2019-09-06 11:10:05', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(72, '2019-09-06 11:10:35', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(73, '2019-09-06 11:10:35', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(74, '2019-09-06 11:11:26', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(75, '2019-09-06 11:11:26', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(76, '2019-09-06 11:11:56', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL),
(77, '2019-09-06 11:11:56', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(78, '2019-09-06 11:12:34', NULL, 2, 'FP-2/report/self', '[\"2019-08-27 10:22:37.912656\", \"status\", \"offline\"]', 'FP-2', 1, NULL),
(79, '2019-09-06 11:12:34', NULL, 1, 'FP-1/report/self', '[\"2019-09-06 13:32:07.636202\", \"status\", \"offline\"]', 'FP-1', 1, NULL);

-- --------------------------------------------------------

--
-- Структура таблицы `clients`
--

CREATE TABLE `clients` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `is_active` tinyint(4) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `clients`
--

INSERT INTO `clients` (`id`, `name`, `is_active`) VALUES
(1, 'Сбербанк', 1),
(2, 'Тинькофф', 1),
(3, 'какой то клиент', 1),
(4, 'АТМ', 1),
(5, 'Газпромбанк', 1);

-- --------------------------------------------------------

--
-- Структура таблицы `commands`
--

CREATE TABLE `commands` (
  `id` int(11) NOT NULL,
  `device` int(11) NOT NULL COMMENT 'идентификатор устройства',
  `command` varchar(8) NOT NULL COMMENT 'команда для устройства',
  `args` text COMMENT 'JSON-строка с уточняющими данными для исполнения команды',
  `formed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'время формирования команды',
  `executed_at` timestamp NULL DEFAULT NULL COMMENT 'время завершения исполнения команды',
  `execution_flag` tinyint(1) NOT NULL COMMENT 'флаг успеха исполнения'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `config`
--

CREATE TABLE `config` (
  `id` int(11) NOT NULL,
  `name` varchar(80) NOT NULL,
  `code` varchar(40) NOT NULL,
  `comment` varchar(80) NOT NULL,
  `value` varchar(16) NOT NULL,
  `datatype_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `config`
--

INSERT INTO `config` (`id`, `name`, `code`, `comment`, `value`, `datatype_id`, `group_id`) VALUES
(1, 'название приложения', 'app_name', 'закешировано', 'FOCUS', 1, 2),
(2, 'частота обновления состояния доступных устройств', 'monitoring_update_interval', 'в секундах', '5', 2, 1);

-- --------------------------------------------------------

--
-- Структура таблицы `config_datatypes`
--

CREATE TABLE `config_datatypes` (
  `id` int(11) NOT NULL,
  `type` varchar(16) NOT NULL,
  `name` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `config_datatypes`
--

INSERT INTO `config_datatypes` (`id`, `type`, `name`) VALUES
(1, 'string', 'строка'),
(2, 'integer', 'целое число'),
(3, 'js_function', 'функция JS');

-- --------------------------------------------------------

--
-- Структура таблицы `config_groups`
--

CREATE TABLE `config_groups` (
  `id` int(11) NOT NULL,
  `name` varchar(16) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `config_groups`
--

INSERT INTO `config_groups` (`id`, `name`) VALUES
(1, 'Мониторинг'),
(2, 'Приложение');

-- --------------------------------------------------------

--
-- Структура таблицы `devices`
--

CREATE TABLE `devices` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `comment` longtext NOT NULL,
  `client_id` int(11) NOT NULL,
  `snmp_host` varchar(100) DEFAULT '',
  `snmp_community` varchar(100) DEFAULT '',
  `snmp_version` varchar(100) DEFAULT '',
  `snmp_user` varchar(100) DEFAULT '',
  `snmp_password` varchar(100) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `devices`
--

INSERT INTO `devices` (`id`, `name`, `address`, `comment`, `client_id`, `snmp_host`, `snmp_community`, `snmp_version`, `snmp_user`, `snmp_password`) VALUES
(-1, 'FP-0', '', 'Используется для описания параметров по умолчанию', 1, '', '', '', '', ''),
(1, 'FP-1', 'город Омск улица Мира 33А кабинет 503', '', 4, '192.168.3.199:161', 'public', '2c', 'user', 'password'),
(2, 'FP-2', 'г.  Павлодар', 'Виртуальная \"Малинка\" на рабочем компьютере.', 4, '127.0.0.1:161', 'public', '2c', 'user', 'psw'),
(23, 'FP-23', '', '', 4, '', '', '', '', '');

--
-- Триггеры `devices`
--
DELIMITER $$
CREATE TRIGGER `devices_insert_before` BEFORE INSERT ON `devices` FOR EACH ROW BEGIN
	SET @lastID = (SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_NAME = "devices");
	set NEW.name = CONCAT('FP-', @lastID);
	
	#if NEW.snmp_host is NULL THEN set NEW.snmp_host = ""; END IF;	#if NEW.snmp_community is NULL THEN set NEW.snmp_community = ""; END IF;	#if NEW.snmp_version is NULL THEN set NEW.snmp_version = ""; END IF;END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Структура таблицы `devices_config`
--

CREATE TABLE `devices_config` (
  `id` int(11) NOT NULL,
  `pin` smallint(6) NOT NULL,
  `format` longtext,
  `device_id` int(11) NOT NULL,
  `unit_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `devices_config`
--

INSERT INTO `devices_config` (`id`, `pin`, `format`, `device_id`, `unit_id`) VALUES
(1, 0, NULL, 1, 1),
(2, 17, NULL, 1, 2),
(3, 27, NULL, 1, 3),
(4, 21, NULL, 1, 4),
(5, 18, NULL, 1, 5),
(6, 23, NULL, 1, 6),
(7, 24, NULL, 1, 7),
(8, 25, NULL, 1, 8),
(9, 5, NULL, 1, 9),
(10, 6, NULL, 1, 10),
(11, 13, NULL, 1, 11),
(12, 19, NULL, 1, 12),
(13, 26, NULL, 1, 13),
(14, 12, NULL, 1, 14),
(15, 16, NULL, 1, 15),
(16, 20, NULL, 1, 16),
(17, 0, NULL, 1, 17),
(18, 0, NULL, 1, 18),
(19, 9, NULL, 1, 19),
(20, 11, NULL, 1, 20),
(21, 0, NULL, 2, 1),
(22, 17, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 2),
(23, 27, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 3),
(24, 21, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 4),
(25, 18, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 5),
(26, 23, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 6),
(27, 24, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 7),
(28, 25, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 8),
(29, 5, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 9),
(30, 6, NULL, 2, 10),
(31, 13, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 11),
(32, 19, '{\"title\": \"Контроль 2\", \"type\": \"INTEGER\", \"chart\": \"area\", \"controls\": [\"toggle\"], \"values\": [{\"value\": \"0\", \"title\": \"Выключен\", \"class\": \"bg-secondary text-white\"}, {\"value\": \"1\", \"title\": \"Включен\", \"class\": \"bg-success text-white\"}, {\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 12),
(33, 26, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 13),
(34, 12, '{\"title\": \"Контроль 3\", \"type\": \"INTEGER\", \"chart\": \"area\", \"controls\": [\"toggle\"], \"values\": [{\"value\": \"0\", \"title\": \"Выключен\", \"class\": \"bg-secondary text-white\"}, {\"value\": \"1\", \"title\": \"Включен\", \"class\": \"bg-success text-white\"}, {\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 14),
(35, 16, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 15),
(36, 20, '{\"title\": \"Контроль 4\", \"type\": \"INTEGER\", \"chart\": \"area\", \"controls\": [\"toggle\"], \"values\": [{\"value\": \"0\", \"title\": \"Выключен\", \"class\": \"bg-secondary text-white\"}, {\"value\": \"1\", \"title\": \"Включен\", \"class\": \"bg-success text-white\"}, {\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 16),
(37, 0, NULL, 2, 17),
(38, 0, NULL, 2, 18),
(39, 9, '{\"title\": \"\", \"type\": \"INTEGER\", \"chart\": \"\", \"controls\": [], \"values\": [{\"value\": \"иначе\", \"title\": \"Неизвестно\", \"class\": \"bg-light text-dark\"}], \"is_default\": false}', 2, 19),
(40, 11, NULL, 2, 20),
(92, 0, NULL, -1, 1),
(93, 17, NULL, -1, 2),
(94, 27, NULL, -1, 3),
(95, 21, NULL, -1, 4),
(96, 18, NULL, -1, 5),
(97, 23, NULL, -1, 6),
(98, 24, NULL, -1, 7),
(99, 25, NULL, -1, 8),
(100, 5, NULL, -1, 9),
(101, 6, NULL, -1, 10),
(102, 13, NULL, -1, 11),
(103, 19, NULL, -1, 12),
(104, 26, NULL, -1, 13),
(105, 12, NULL, -1, 14),
(106, 16, NULL, -1, 15),
(107, 20, NULL, -1, 16),
(108, 0, NULL, -1, 17),
(109, 0, NULL, -1, 18),
(110, 9, NULL, -1, 19),
(111, 11, NULL, -1, 20),
(1084, -1, NULL, 23, 10),
(1085, -1, NULL, 23, 12),
(1086, -1, NULL, 23, 14),
(1087, -1, NULL, 23, 16),
(1088, -1, NULL, 23, 9),
(1089, -1, NULL, 23, 11),
(1090, -1, NULL, 23, 13),
(1091, -1, NULL, 23, 15),
(1092, -1, NULL, 23, 4),
(1093, -1, NULL, 23, 5),
(1094, -1, NULL, 23, 6),
(1095, -1, NULL, 23, 7),
(1096, -1, NULL, 23, 8),
(1097, -1, NULL, 23, 2),
(1098, -1, NULL, 23, 3),
(1099, -1, NULL, 23, 20),
(1100, -1, NULL, 23, 19);

-- --------------------------------------------------------

--
-- Структура таблицы `device_routines`
--

CREATE TABLE `device_routines` (
  `id` int(11) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `instruction` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `device_routines`
--

INSERT INTO `device_routines` (`id`, `device_id`, `name`, `comment`, `instruction`) VALUES
(3, 1, 'включение вентилятора', '', '{\"routine\": {\"conditions\": [{\"unit\": \"cpu\", \"compare\": \"gt\", \"value\": \"60\"}], \"actions\": [{\"action\": \"setValue\", \"unit\": \"out4\", \"value\": \"1\"}]}}'),
(8, 1, 'перезагрузка', '', '{\"routine\": {\"conditions\": [{\"unit\": \"in1\", \"compare\": \"eq\", \"value\": \"1\"}, \"and\", {\"unit\": \"in5\", \"compare\": \"lt\", \"value\": \"50\"}], \"actions\": [{\"action\": \"call\", \"unit\": \"\", \"value\": \"\", \"function\": \"reboot\", \"params\": []}]}}'),
(14, 1, 'включение вентилятора малинки', 'на малинке должна существовать функция run_fan(speed, min_temp)', '{\"routine\": {\"conditions\": [[{\"unit\": \"in1\", \"compare\": \"eq\", \"value\": \"0\"}, \"and\", {\"unit\": \"in2\", \"compare\": \"eq\", \"value\": \"1\"}], \"or\", {\"unit\": \"cpu\", \"compare\": \"gt\", \"value\": \"80\"}], \"actions\": [{\"action\": \"call\", \"unit\": \"\", \"value\": \"\", \"function\": \"run_fan\", \"params\": [{\"name\": \"speed\", \"value\": \"500\"}, {\"name\": \"min_temp\", \"value\": \"60\"}]}]}}');

-- --------------------------------------------------------

--
-- Структура таблицы `device_routines_builtin`
--

CREATE TABLE `device_routines_builtin` (
  `id` int(11) NOT NULL,
  `device_id` int(11) DEFAULT NULL COMMENT 'ID устройства',
  `name` varchar(255) DEFAULT NULL COMMENT 'название функции',
  `params` text COMMENT 'описание параметров функции',
  `comment` varchar(255) DEFAULT NULL COMMENT 'комментарий'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Команды, которые можно вызвать на удаленном устройстве';

--
-- Дамп данных таблицы `device_routines_builtin`
--

INSERT INTO `device_routines_builtin` (`id`, `device_id`, `name`, `params`, `comment`) VALUES
(1, -1, 'reboot', '[]', 'перезагрузка устройства'),
(2, -1, 'run_fan', '[\n	{\n		\"name\": \"speed\",\n		\"value\": \"150\",\n		\"desc\": \"число оборотов\"\n	},\n	{\n		\"name\": \"min_temp\",\n		\"value\": \"50\",\n		\"desc\": \"температу, при которой отключать датчик\"\n	}\n]', 'включение системы охлаждения (вентилятор)'),
(3, 1, 'fp_1_reboot', '[\n	{\n		\"name\": \"param1\",\n		\"value\": \"\",\n		\"desc\": \"описание параметра\"\n	}\n]', 'функция, доступная только для FP-1');

-- --------------------------------------------------------

--
-- Структура таблицы `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(1, '2019-07-01 07:48:44.264068', '1', 'Client object (1)', 1, '[{\"added\": {}}]', 7, 1),
(2, '2019-07-01 07:50:10.170055', '2', 'Тинькоф', 1, '[{\"added\": {}}]', 7, 1),
(3, '2019-07-01 07:50:19.646351', '3', 'Мираф', 1, '[{\"added\": {}}]', 7, 1),
(4, '2019-07-01 07:54:26.132939', '1', 'Сбербанк', 1, '[{\"added\": {}}]', 8, 1),
(5, '2019-07-01 07:54:32.925921', '2', 'Тинькоф', 1, '[{\"added\": {}}]', 8, 1),
(6, '2019-07-01 09:50:17.988454', '1', 'errr', 1, '[{\"added\": {}}]', 9, 1),
(7, '2019-07-01 09:53:37.869846', '1', 'wewewe', 1, '[{\"added\": {}}]', 9, 1),
(8, '2019-07-01 11:24:04.788809', '1', 'Администратор', 1, '[{\"added\": {}}]', 11, 1),
(9, '2019-07-01 11:24:23.854129', '10', 'роль 1', 1, '[{\"added\": {}}]', 11, 1),
(10, '2019-07-01 11:27:40.842797', '1', 'Администратор', 1, '[{\"added\": {}}]', 11, 1),
(11, '2019-07-01 11:27:55.644540', '10', 'Роль 1', 1, '[{\"added\": {}}]', 11, 1),
(12, '2019-07-01 11:29:56.404942', '8', 'ATM', 1, '[{\"added\": {}}]', 8, 1),
(13, '2019-07-01 11:39:05.104028', '2', 'ИвановИван', 1, '[{\"added\": {}}]', 10, 1),
(14, '2019-07-02 04:50:29.836716', '1', 'Управление', 1, '[{\"added\": {}}]', 12, 1),
(15, '2019-07-02 04:50:38.654604', '2', 'Клиенты', 1, '[{\"added\": {}}]', 12, 1),
(16, '2019-07-02 06:06:59.284239', '1', 'Управление', 1, '[{\"added\": {}}]', 3, 1),
(17, '2019-07-02 06:07:08.250528', '2', 'Клиены', 1, '[{\"added\": {}}]', 3, 1),
(18, '2019-07-02 06:24:23.040262', '49', 'Clients | clients | Клиенты. Редактирование', 1, '[{\"added\": {}}]', 2, 1),
(19, '2019-07-02 06:25:01.989706', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(20, '2019-07-02 06:26:55.211248', '50', 'Clients | clients | Клиенты. Просмотр информации', 1, '[{\"added\": {}}]', 2, 1),
(21, '2019-07-02 06:27:12.641342', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(22, '2019-07-02 06:28:02.370876', '51', 'Clients | clients | Клиенты. Добавление', 1, '[{\"added\": {}}]', 2, 1),
(23, '2019-07-02 06:28:13.354129', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(24, '2019-07-02 06:29:06.203410', '52', 'Clients | clients | Клиенты. Просмотр списка', 1, '[{\"added\": {}}]', 2, 1),
(25, '2019-07-02 06:30:00.670832', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(26, '2019-07-02 06:30:18.421019', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(27, '2019-07-02 06:35:59.910615', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(28, '2019-07-02 06:38:19.598135', '53', 'Devices | devices | Оборудование. Просмотр списка', 1, '[{\"added\": {}}]', 2, 1),
(29, '2019-07-02 06:39:55.601250', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(30, '2019-07-02 06:40:53.124103', '57', 'Profiles | profiles | Пользователи. Просмотр списка', 1, '[{\"added\": {}}]', 2, 1),
(31, '2019-07-02 06:42:32.226176', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(32, '2019-07-02 06:44:51.813901', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(33, '2019-07-02 06:45:07.170273', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(34, '2019-07-02 06:47:44.119190', '1', 'Управление', 2, '[{\"changed\": {\"fields\": [\"permissions\"]}}]', 3, 1),
(35, '2019-07-02 06:48:16.809760', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(36, '2019-07-02 06:48:52.570896', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"groups\"]}}]', 4, 1),
(37, '2019-07-02 07:01:18.366005', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"groups\", \"user_permissions\"]}}]', 4, 1),
(38, '2019-07-02 07:02:44.400460', '61', 'Profiles | profiles | Пользователи. Изменение прав доступа', 1, '[{\"added\": {}}]', 2, 1),
(39, '2019-07-02 07:03:02.359512', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(40, '2019-07-02 07:05:08.961982', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(41, '2019-07-02 07:05:31.448454', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(42, '2019-07-02 07:51:25.089468', '2', 'Клиены', 2, '[{\"changed\": {\"fields\": [\"permissions\"]}}]', 3, 1),
(43, '2019-07-02 08:07:54.682668', '1', 'Управление', 2, '[{\"changed\": {\"fields\": [\"permissions\"]}}]', 3, 1),
(44, '2019-07-02 09:06:45.273173', '3', 'maksim_serg_test_2@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(45, '2019-07-02 09:56:49.485632', '3', 'maksim_serg_test_2@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(46, '2019-07-02 10:37:48.052130', '2', 'Клиены', 2, '[{\"changed\": {\"fields\": [\"permissions\"]}}]', 3, 1),
(47, '2019-07-02 10:38:48.656880', '2', 'maksim_serg_test_1@mail.ru', 2, '[{\"changed\": {\"fields\": [\"user_permissions\"]}}]', 4, 1),
(48, '2019-07-02 11:29:26.066574', '66', 'Monitoring | monitoring | Мониторинг', 1, '[{\"added\": {}}]', 2, 1),
(49, '2019-07-02 11:29:50.183966', '2', 'Клиены', 2, '[{\"changed\": {\"fields\": [\"permissions\"]}}]', 3, 1),
(50, '2019-07-04 06:04:36.016362', '1', 'Мониторинг', 1, '[{\"added\": {}}]', 15, 1),
(51, '2019-07-04 06:06:55.634735', '1', 'мониторинг: период обновления', 1, '[{\"added\": {}}]', 14, 1),
(52, '2019-07-04 06:08:15.582512', '1', 'мониторинг: период обновления', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 14, 1),
(53, '2019-07-04 06:09:54.083404', '1', 'мониторинг: период обновления (monitoring_update_period=5) None', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 14, 1),
(54, '2019-07-04 06:10:18.512724', '1', 'мониторинг: период обновления (monitoring_update_period=5)', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 14, 1),
(55, '2019-07-04 06:20:56.041564', 'int', 'целое', 1, '[{\"added\": {}}]', 16, 1),
(56, '2019-07-04 06:21:13.979326', 'js_func', 'js функция', 1, '[{\"added\": {}}]', 16, 1),
(57, '2019-07-04 06:21:31.854507', '1', 'мониторинг: период обновления (monitoring_update_period=5)', 2, '[{\"changed\": {\"fields\": [\"type\"]}}]', 14, 1),
(58, '2019-07-04 06:22:45.046195', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=1)', 1, '[{\"added\": {}}]', 14, 1),
(59, '2019-07-04 06:24:42.870428', 'js_function', 'js функция', 2, '[{\"changed\": {\"fields\": [\"type\"]}}]', 16, 1),
(60, '2019-07-04 06:26:58.126181', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_func)function(value){\r\n          stateClassName = \"\";\r\n         if (value >= 80) {\r\n            stateClassName = \"bg-danger te', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(61, '2019-07-04 06:29:00.458460', '2', 'Приложение', 1, '[{\"added\": {}}]', 15, 1),
(62, '2019-07-04 06:29:22.581316', 'string', 'строка', 1, '[{\"added\": {}}]', 16, 1),
(63, '2019-07-04 06:29:42.655785', '3', 'название приложения (app_name=(string)FOCUS)', 1, '[{\"added\": {}}]', 14, 1),
(64, '2019-07-04 06:43:51.314568', '3', 'название приложения (app_name=(string)FOCUS-2)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(65, '2019-07-04 06:44:14.876661', '3', 'название приложения (app_name=(string)FOCUS)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(66, '2019-07-04 07:31:18.470407', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_func)function(value){\r\n  ...)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(67, '2019-07-04 08:29:27.341762', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(68, '2019-07-04 08:29:43.261610', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(69, '2019-07-04 08:30:05.367082', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(70, '2019-07-04 08:42:22.486621', '2', 'мониторинг: температура процессора цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 2, '[]', 14, 1),
(71, '2019-07-04 08:42:56.658017', '3', 'название приложения (app_name=(string)FOCUS)', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 14, 1),
(72, '2019-07-04 10:03:51.410963', '2', 'мониторинг: температура среды цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 2, '[{\"changed\": {\"fields\": [\"name\", \"value\"]}}]', 14, 1),
(73, '2019-07-04 10:57:14.723551', '1', 'ins', 1, '[{\"added\": {}}]', 18, 1),
(74, '2019-07-04 10:57:23.619510', '2', 'temp', 1, '[{\"added\": {}}]', 18, 1),
(75, '2019-07-04 10:58:23.020136', '1', 'in1', 1, '[{\"added\": {}}]', 17, 1),
(76, '2019-07-04 10:59:09.489213', '6', 'cpu', 1, '[{\"added\": {}}]', 17, 1),
(77, '2019-07-04 10:59:37.320397', '7', 'ext', 1, '[{\"added\": {}}]', 17, 1),
(78, '2019-07-04 10:59:50.347024', '6', 'cpu', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 17, 1),
(79, '2019-07-04 11:15:01.089517', '3', 'out', 1, '[{\"added\": {}}]', 18, 1),
(80, '2019-07-04 11:15:43.920932', '8', 'ou1', 1, '[{\"added\": {}}]', 17, 1),
(81, '2019-07-04 11:36:49.936771', '1', 'Устройство ввода', 1, '[{\"added\": {}}]', 19, 1),
(82, '2019-07-04 11:39:45.354300', '3', 'Устройство вывода, state=0 (Выключено)', 2, '[{\"changed\": {\"fields\": [\"family\"]}}]', 19, 1),
(83, '2019-07-05 03:46:21.595804', '2', 'FP-532067c6:in1', 1, '[{\"added\": {}}]', 20, 1),
(84, '2019-07-05 03:50:32.718945', '2', 'FP-532067c6:in1', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(85, '2019-07-05 04:09:42.142717', '2', 'FP-532067c6:in1', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(86, '2019-07-05 04:57:02.372506', '7', 'ext (Температура среды)', 2, '[{\"changed\": {\"fields\": [\"title\"]}}]', 17, 1),
(87, '2019-07-05 04:57:12.193688', '6', 'cpu (Температура CPU)', 2, '[{\"changed\": {\"fields\": [\"title\"]}}]', 17, 1),
(88, '2019-07-05 09:29:09.505043', '4', 'мониторинг: температура процессора цвет (класс) (monitoring_cpu_class=(js_function)function(value){\r\n  ...)', 3, '', 14, 1),
(89, '2019-07-05 09:29:09.547294', '2', 'мониторинг: температура среды цвет (класс) (monitoring_ext_class=(js_function)function(value){\r\n  ...)', 3, '', 14, 1),
(90, '2019-07-05 09:42:52.623823', '4', 'dev', 1, '[{\"added\": {}}]', 18, 1),
(91, '2019-07-05 09:43:30.526951', '9', 'focuspro (онлайн/оффлайн)', 1, '[{\"added\": {}}]', 17, 1),
(92, '2019-07-05 10:17:49.858446', '2', 'FP-0:in1', 2, '[{\"changed\": {\"fields\": [\"device\"]}}]', 20, 1),
(93, '2019-07-05 10:18:09.415869', '2', 'FP-532067c6:in1', 2, '[{\"changed\": {\"fields\": [\"device\"]}}]', 20, 1),
(94, '2019-07-05 10:18:20.092671', '18', 'FP-0:in1', 1, '[{\"added\": {}}]', 20, 1),
(95, '2019-07-05 10:20:46.219211', '26', 'FP-0:focuspro', 1, '[{\"added\": {}}]', 20, 1),
(96, '2019-07-05 10:23:14.547117', '26', 'FP-0:focuspro', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(97, '2019-07-05 10:23:48.040847', '-1', '[FP-0] Служебный', 2, '[{\"changed\": {\"fields\": [\"client\"]}}]', 9, 1),
(98, '2019-07-05 10:57:22.704330', '26', 'FP-0:focuspro', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(99, '2019-07-05 10:58:13.544901', '26', 'FP-0:focuspro', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(100, '2019-07-05 11:22:26.918879', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)2)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(101, '2019-07-05 11:24:59.923728', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)5)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(102, '2019-07-05 11:27:26.968527', '5', '[FP-42dfbad7] Банкомат-тест', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(103, '2019-07-05 11:28:00.158363', '6', '[FP-37a2e02c] qqq', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(104, '2019-07-05 11:29:57.975045', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)1000)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(105, '2019-07-05 11:48:27.239112', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)5)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(106, '2019-07-05 11:48:37.891126', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)15)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(107, '2019-07-05 11:48:50.500613', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)1000)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(108, '2019-07-05 11:54:48.870263', '26', 'FP-0:focuspro', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(109, '2019-07-05 11:55:21.083052', '26', 'FP-0:focuspro', 2, '[{\"changed\": {\"fields\": [\"state\"]}}]', 20, 1),
(110, '2019-07-05 11:57:17.662289', '1', '[FP-e4f2728d] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(111, '2019-07-08 09:15:08.494517', '1', '[FP-70666c90] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(112, '2019-07-09 04:53:30.220495', '1', '[FP-6b915047] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(113, '2019-07-09 06:52:04.948414', '1', '[FP-e3629564] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(114, '2019-07-09 08:29:40.267761', '1', '[FP-2bb78baa] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(115, '2019-07-09 09:34:15.551468', '3', 'couts', 2, '[{\"changed\": {\"fields\": [\"name\"]}}]', 18, 1),
(116, '2019-07-09 09:35:07.738106', '8', 'cmp1/event', 2, '[{\"changed\": {\"fields\": [\"name\"]}}]', 17, 1),
(117, '2019-07-09 11:36:04.645682', '1', '[FP-8bbaeb43] Банкомат', 2, '[{\"changed\": {\"fields\": [\"uid\"]}}]', 9, 1),
(118, '2019-07-16 04:57:15.184140', '7', '[FP-7] hjhgjhg', 3, '', 9, 1),
(119, '2019-07-16 04:57:15.230854', '6', '[FP-6] qqq', 3, '', 9, 1),
(120, '2019-07-16 04:57:15.277733', '5', '[FP-5] Банкомат-тест', 3, '', 9, 1),
(121, '2019-07-16 08:52:07.886189', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)2)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(122, '2019-07-16 08:54:20.076726', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)4)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(123, '2019-07-16 09:12:58.093627', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)5)', 2, '[{\"changed\": {\"fields\": [\"value\"]}}]', 14, 1),
(124, '2019-07-17 03:36:25.522766', '1', 'мониторинг: период обновления (monitoring_update_period=(integer)5)', 2, '[{\"changed\": {\"fields\": [\"comment\"]}}]', 14, 4),
(125, '2019-07-29 10:57:35.666110', '3', 'FP-2', 1, '[{\"added\": {}}]', 26, 4),
(126, '2019-07-29 11:03:42.249207', '2', 'Клиенты', 2, '[{\"changed\": {\"fields\": [\"name\"]}}]', 3, 4),
(127, '2019-07-29 11:06:22.608509', '25', 'Client | client | Can add client', 3, '', 2, 4),
(128, '2019-07-29 11:06:22.654913', '26', 'Client | client | Can change client', 3, '', 2, 4),
(129, '2019-07-29 11:06:22.701764', '27', 'Client | client | Can delete client', 3, '', 2, 4),
(130, '2019-07-29 11:06:22.748699', '28', 'Client | client | Can view client', 3, '', 2, 4),
(131, '2019-07-29 11:06:22.795328', '29', 'Clients | clients | Can add clients', 3, '', 2, 4),
(132, '2019-07-29 11:06:22.842036', '30', 'Clients | clients | Can change clients', 3, '', 2, 4),
(133, '2019-07-29 11:06:22.889262', '51', 'Clients | clients | Клиенты. Добавление', 3, '', 2, 4),
(134, '2019-07-29 11:06:22.936242', '49', 'Clients | clients | Клиенты. Редактирование', 3, '', 2, 4),
(135, '2019-07-29 11:06:22.983880', '52', 'Clients | clients | Клиенты. Просмотр списка', 3, '', 2, 4),
(136, '2019-07-29 11:06:23.030893', '50', 'Clients | clients | Клиенты. Просмотр информации', 3, '', 2, 4),
(137, '2019-07-29 11:06:23.080517', '31', 'Clients | clients | Can delete clients', 3, '', 2, 4),
(138, '2019-07-29 11:06:23.130137', '32', 'Clients | clients | Can view clients', 3, '', 2, 4),
(139, '2019-07-29 11:06:23.178209', '33', 'Devices | devices | Can add devices', 3, '', 2, 4),
(140, '2019-07-29 11:06:23.225216', '34', 'Devices | devices | Can change devices', 3, '', 2, 4),
(141, '2019-07-29 11:06:23.271716', '35', 'Devices | devices | Can delete devices', 3, '', 2, 4),
(142, '2019-07-29 11:06:23.317938', '56', 'Devices | devices | Оборудование. Добавление', 3, '', 2, 4),
(143, '2019-07-29 11:06:23.364120', '54', 'Devices | devices | Оборудование. Редактирование', 3, '', 2, 4),
(144, '2019-07-29 11:06:23.410661', '53', 'Devices | devices | Оборудование. Просмотр списка', 3, '', 2, 4),
(145, '2019-07-29 11:06:23.457403', '55', 'Devices | devices | Оборудование. Просмотр информации', 3, '', 2, 4),
(146, '2019-07-29 11:06:23.504161', '36', 'Devices | devices | Can view devices', 3, '', 2, 4),
(147, '2019-07-29 11:06:23.550605', '91', 'DeviceUnits | clientunits | Can add client units', 3, '', 2, 4),
(148, '2019-07-29 11:06:23.597188', '92', 'DeviceUnits | clientunits | Can change client units', 3, '', 2, 4),
(149, '2019-07-29 11:06:23.643888', '93', 'DeviceUnits | clientunits | Can delete client units', 3, '', 2, 4),
(150, '2019-07-29 11:06:23.690555', '94', 'DeviceUnits | clientunits | Can view client units', 3, '', 2, 4),
(151, '2019-07-29 11:06:23.737179', '83', 'DeviceUnits | family | Can add family', 3, '', 2, 4),
(152, '2019-07-29 11:06:23.783931', '84', 'DeviceUnits | family | Can change family', 3, '', 2, 4),
(153, '2019-07-29 11:06:23.830837', '85', 'DeviceUnits | family | Can delete family', 3, '', 2, 4),
(154, '2019-07-29 11:06:23.877575', '86', 'DeviceUnits | family | Can view family', 3, '', 2, 4),
(155, '2019-07-29 11:06:23.924549', '95', 'DeviceUnits | gpioconfig | Can add gpio config', 3, '', 2, 4),
(156, '2019-07-29 11:06:23.971464', '96', 'DeviceUnits | gpioconfig | Can change gpio config', 3, '', 2, 4),
(157, '2019-07-29 11:06:24.018416', '97', 'DeviceUnits | gpioconfig | Can delete gpio config', 3, '', 2, 4),
(158, '2019-07-29 11:06:24.065146', '98', 'DeviceUnits | gpioconfig | Can view gpio config', 3, '', 2, 4),
(159, '2019-07-29 11:06:24.112244', '87', 'DeviceUnits | meter | Can add meter', 3, '', 2, 4),
(160, '2019-07-29 11:06:24.159147', '88', 'DeviceUnits | meter | Can change meter', 3, '', 2, 4),
(161, '2019-07-29 11:06:24.206020', '89', 'DeviceUnits | meter | Can delete meter', 3, '', 2, 4),
(162, '2019-07-29 11:06:24.252773', '90', 'DeviceUnits | meter | Can view meter', 3, '', 2, 4),
(163, '2019-07-29 11:06:24.299001', '79', 'DeviceUnits | units | Can add units', 3, '', 2, 4),
(164, '2019-07-29 11:06:24.344514', '80', 'DeviceUnits | units | Can change units', 3, '', 2, 4),
(165, '2019-07-29 11:06:24.390416', '81', 'DeviceUnits | units | Can delete units', 3, '', 2, 4),
(166, '2019-07-29 11:06:24.436697', '82', 'DeviceUnits | units | Can view units', 3, '', 2, 4),
(167, '2019-07-29 11:06:24.483212', '62', 'Monitoring | monitoring | Can add monitoring', 3, '', 2, 4),
(168, '2019-07-29 11:06:24.530110', '63', 'Monitoring | monitoring | Can change monitoring', 3, '', 2, 4),
(169, '2019-07-29 11:06:24.576800', '64', 'Monitoring | monitoring | Can delete monitoring', 3, '', 2, 4),
(170, '2019-07-29 11:06:24.623280', '66', 'Monitoring | monitoring | Мониторинг', 3, '', 2, 4),
(171, '2019-07-29 11:06:24.669930', '65', 'Monitoring | monitoring | Can view monitoring', 3, '', 2, 4);

-- --------------------------------------------------------

--
-- Структура таблицы `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  `auth_group_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`, `auth_group_id`) VALUES
(1, 'admin', 'logentry', NULL),
(2, 'auth', 'permission', NULL),
(3, 'auth', 'group', NULL),
(4, 'auth', 'user', NULL),
(5, 'contenttypes', 'contenttype', NULL),
(6, 'sessions', 'session', NULL),
(7, 'Client', 'client', NULL),
(8, 'Clients', 'clients', NULL),
(9, 'Devices', 'devices', NULL),
(10, 'Profiles', 'profiles', NULL),
(11, 'Roles', 'roles', NULL),
(12, 'Roles', 'group', NULL),
(13, 'Monitoring', 'monitoring', NULL),
(14, 'Settings', 'settings', NULL),
(15, 'Settings', 'groups', NULL),
(16, 'Settings', 'types', NULL),
(17, 'DeviceUnits', 'units', NULL),
(18, 'DeviceUnits', 'family', NULL),
(19, 'DeviceUnits', 'meter', NULL),
(20, 'DeviceUnits', 'clientunits', NULL),
(21, 'DeviceUnits', 'gpioconfig', NULL),
(22, 'configuration', 'group', NULL),
(23, 'configuration', 'datatype', NULL),
(24, 'configuration', 'configuration', NULL),
(25, 'clients', 'client', NULL),
(26, 'devices', 'device', NULL),
(27, 'devices', 'config', NULL),
(28, 'monitoring', 'monitor', NULL),
(29, 'profiles', 'profile', NULL),
(30, 'roles', 'role', NULL),
(31, 'units', 'family', NULL),
(32, 'units', 'unit', NULL),
(33, 'status', 'status', NULL),
(34, 'events', 'event', NULL),
(35, 'msg_types', 'message', NULL),
(37, 'Клиенты', 'app.clients', 1),
(38, 'Устройства', 'app.devices', 2),
(39, 'Пользователи', 'app.users', 2),
(40, 'Мониторинг', 'app.monitoring', 2);

-- --------------------------------------------------------

--
-- Структура таблицы `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2019-07-01 06:45:14.503824'),
(2, 'auth', '0001_initial', '2019-07-01 06:45:15.978102'),
(3, 'admin', '0001_initial', '2019-07-01 06:45:17.131075'),
(4, 'admin', '0002_logentry_remove_auto_add', '2019-07-01 06:45:17.356880'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2019-07-01 06:45:17.465839'),
(6, 'contenttypes', '0002_remove_content_type_name', '2019-07-01 06:45:17.828424'),
(7, 'auth', '0002_alter_permission_name_max_length', '2019-07-01 06:45:17.985305'),
(8, 'auth', '0003_alter_user_email_max_length', '2019-07-01 06:45:18.152355'),
(9, 'auth', '0004_alter_user_username_opts', '2019-07-01 06:45:18.259349'),
(10, 'auth', '0005_alter_user_last_login_null', '2019-07-01 06:45:18.404447'),
(11, 'auth', '0006_require_contenttypes_0002', '2019-07-01 06:45:18.488499'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2019-07-01 06:45:18.591369'),
(13, 'auth', '0008_alter_user_username_max_length', '2019-07-01 06:45:18.755748'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2019-07-01 06:45:18.919039'),
(15, 'auth', '0010_alter_group_name_max_length', '2019-07-01 06:45:19.085435'),
(16, 'auth', '0011_update_proxy_permissions', '2019-07-01 06:45:19.307536'),
(17, 'sessions', '0001_initial', '2019-07-01 06:45:19.566102'),
(18, 'Client', '0001_initial', '2019-07-01 07:46:44.636246'),
(19, 'Clients', '0001_initial', '2019-07-01 07:53:54.308711'),
(20, 'Clients', '0002_auto_20190701_0753', '2019-07-01 07:53:54.628118'),
(28, 'Devices', '0001_initial', '2019-07-01 09:53:12.953062'),
(29, 'Devices', '0002_auto_20190701_1006', '2019-07-01 10:06:09.723067'),
(30, 'Devices', '0003_auto_20190701_1043', '2019-07-01 10:43:42.862783'),
(31, 'Devices', '0004_devices_uid', '2019-07-01 10:46:04.677100'),
(32, 'Profiles', '0001_initial', '2019-07-01 10:58:02.310373'),
(34, 'Roles', '0001_initial', '2019-07-01 11:20:59.303858'),
(35, 'Roles', '0002_auto_20190701_1123', '2019-07-01 11:23:39.311122'),
(36, 'Roles', '0003_auto_20190701_1127', '2019-07-01 11:27:17.843453'),
(37, 'Profiles', '0002_profiles_role', '2019-07-01 11:29:15.657886'),
(38, 'Profiles', '0003_auto_20190701_1140', '2019-07-01 11:40:56.317129'),
(39, 'Roles', '0004_auto_20190702_0448', '2019-07-02 04:49:13.922986'),
(40, 'Roles', '0005_auto_20190702_0448', '2019-07-02 04:49:14.016266'),
(41, 'Roles', '0006_auto_20190702_0452', '2019-07-02 04:52:36.190138'),
(42, 'Roles', '0007_auto_20190702_0452', '2019-07-02 04:52:58.400537'),
(43, 'Profiles', '0004_auto_20190702_0818', '2019-07-02 08:20:32.918504'),
(44, 'Profiles', '0005_auto_20190702_1031', '2019-07-02 10:31:45.284223'),
(45, 'Profiles', '0006_auto_20190702_1032', '2019-07-02 10:32:01.333465'),
(46, 'Settings', '0001_initial', '2019-07-04 06:04:08.321963'),
(47, 'Settings', '0002_settings_code', '2019-07-04 06:06:07.818222'),
(48, 'Settings', '0003_settings_comment', '2019-07-04 06:07:33.347931'),
(49, 'Settings', '0004_auto_20190704_0607', '2019-07-04 06:07:59.361751'),
(50, 'Settings', '0005_auto_20190704_0613', '2019-07-04 06:13:24.326940'),
(51, 'Settings', '0006_auto_20190704_0620', '2019-07-04 06:20:24.991863'),
(52, 'Settings', '0007_auto_20190704_0632', '2019-07-04 06:32:29.446362'),
(53, 'DeviceUnits', '0001_initial', '2019-07-04 10:56:48.461302'),
(54, 'DeviceUnits', '0002_auto_20190704_1106', '2019-07-04 11:06:45.332027'),
(55, 'DeviceUnits', '0003_meter', '2019-07-04 11:33:34.364760'),
(56, 'DeviceUnits', '0004_meter_code', '2019-07-04 11:36:13.411297'),
(57, 'DeviceUnits', '0005_auto_20190704_1155', '2019-07-04 11:55:46.619937'),
(58, 'DeviceUnits', '0006_auto_20190705_0342', '2019-07-05 03:42:14.400118'),
(59, 'DeviceUnits', '0007_auto_20190705_0404', '2019-07-05 04:04:05.873658'),
(60, 'DeviceUnits', '0008_auto_20190705_0544', '2019-07-05 05:44:25.227140'),
(61, 'DeviceUnits', '0009_clientunits_is_custom', '2019-07-05 09:33:59.931878'),
(62, 'DeviceUnits', '0010_auto_20190705_0934', '2019-07-05 09:34:49.401287'),
(63, 'DeviceUnits', '0011_units_comment', '2019-07-12 10:39:35.687376'),
(64, 'DeviceUnits', '0012_family_comment', '2019-07-12 10:41:27.973404'),
(65, 'DeviceUnits', '0013_auto_20190712_1045', '2019-07-12 10:46:00.593774'),
(66, 'DeviceUnits', '0014_auto_20190712_1046', '2019-07-12 10:46:48.059809'),
(67, 'DeviceUnits', '0015_gpioconfig', '2019-07-12 11:01:13.559160'),
(68, 'DeviceUnits', '0016_units_format', '2019-07-15 04:52:04.809379'),
(69, 'DeviceUnits', '0017_auto_20190715_0502', '2019-07-15 05:02:17.261394'),
(70, 'DeviceUnits', '0018_auto_20190715_0806', '2019-07-15 08:06:33.772132'),
(71, 'DeviceUnits', '0019_units_is_pin', '2019-07-15 08:09:21.143469'),
(72, 'DeviceUnits', '0020_auto_20190717_0339', '2019-07-17 03:41:06.937378'),
(73, 'Monitoring', '0001_initial', '2019-07-17 03:41:07.114130'),
(74, 'Profiles', '0007_auto_20190717_0339', '2019-07-17 03:41:07.334194'),
(75, 'configuration', '0001_initial', '2019-07-26 03:34:24.582184'),
(76, 'configuration', '0002_auto_20190726_1105', '2019-07-26 05:05:34.087980'),
(77, 'clients', '0001_initial', '2019-07-26 05:09:24.069796'),
(78, 'units', '0001_initial', '2019-07-26 05:09:24.792909'),
(79, 'devices', '0001_initial', '2019-07-26 05:09:25.509745'),
(80, 'profiles', '0001_initial', '2019-07-26 05:10:31.809420'),
(81, 'roles', '0001_initial', '2019-07-26 05:10:32.972020'),
(82, 'profiles', '0002_auto_20190726_1122', '2019-07-26 05:23:07.371308'),
(83, 'roles', '0002_auto_20190726_1129', '2019-07-26 05:29:08.726342'),
(84, 'clients', '0002_auto_20190726_1344', '2019-07-26 07:48:55.380292'),
(85, 'configuration', '0003_auto_20190726_1344', '2019-07-26 07:48:55.512525'),
(86, 'devices', '0002_auto_20190726_1344', '2019-07-26 07:48:55.642035'),
(87, 'profiles', '0003_auto_20190726_1348', '2019-07-26 07:48:55.774251'),
(88, 'roles', '0003_auto_20190726_1348', '2019-07-26 07:48:55.898480'),
(89, 'units', '0002_auto_20190726_1348', '2019-07-26 07:48:56.019345'),
(90, 'profiles', '0004_auto_20190726_1353', '2019-07-26 07:53:27.555914'),
(91, 'devices', '0003_auto_20190801_1251', '2019-08-01 06:51:41.032087'),
(92, 'units', '0003_auto_20190801_1251', '2019-08-01 06:51:41.217042'),
(93, 'devices', '0004_auto_20190807_1233', '2019-08-07 06:33:16.177597'),
(94, 'units', '0004_auto_20190807_1233', '2019-08-07 06:33:16.445170'),
(95, 'status', '0001_initial', '2019-08-23 09:45:49.207323'),
(96, 'status', '0002_auto_20190823_1540', '2019-08-23 09:45:49.289760'),
(97, 'events', '0001_initial', '2019-08-23 10:55:18.769053'),
(98, 'msg_types', '0001_initial', '2019-08-23 10:55:30.172344');

-- --------------------------------------------------------

--
-- Структура таблицы `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('1est10m96kheikqnkb3lu2s9jplr8ta6', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-19 03:33:10.583984'),
('1vwqhi4h48gndaopwp1sz3l7mh058lk1', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-13 09:16:19.268228'),
('2r7r3ug6pupyvhi20etngffrzlqxigfo', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-09-09 03:25:08.810090'),
('3orpoitiadv0jqvuz06c80fewit237yu', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-17 04:41:42.818187'),
('68bftu1i52xmjs2ptf18vwa3lbp7w88y', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-12 09:58:55.353850'),
('bpna29j2fmcm0a02xeqe8rvq3dx24hc0', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-09-01 15:52:19.915685'),
('dkwmcj563xo27tydyrfzs7unztasyu8m', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-12 11:43:52.997915'),
('f7pu4ffurfhxzcoij2221btdzytapqz3', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-08-23 11:31:20.130170'),
('iaasy4bmb63zv0q7cyrn8widdlosxfif', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-08-27 04:07:52.493892'),
('ibexcb0cgx7hrdp3gjoyxelw1trpct9d', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-09-06 08:21:20.947548'),
('iwqylnxdys56n702jw9gojapjd9loc2b', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-08-14 10:29:25.703461'),
('jcj1js2h5msp8ubgt95ik7xgcwov3u07', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-12 11:09:40.768114'),
('kq7jdumva66raix12maivbbxbbx3cbpd', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-07-16 10:40:03.999076'),
('l04u2l8q4n7ncntldzvorr9andjo8ojn', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-13 11:35:58.447418'),
('mvu8n8bod8bzj2y7zyap5h5m1ulbf0y5', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-07-17 03:28:47.587302'),
('nomxhlgh84gz0mq0qwb1h6tiqwq6ko7q', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-19 06:59:46.879231'),
('o5budjfvv1pu6cy06ykz660hzcpcpyzs', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-09-11 03:57:03.088636'),
('qhm2bai6n8za1qjim55o00ar9111dj53', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-09-10 04:21:06.496671'),
('qjdrl653a6czcuzplm8ghr5sri65v8ib', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-13 05:28:38.399478'),
('riexfrpa2sn21a8ukuwe9j6s3ig33y16', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-08-20 05:44:14.698694'),
('s0kbq6qrhv5ujc4pzsag8unh3xpm54kt', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-08-22 09:31:01.976410'),
('tkntluikminomebk8iuajdmpl3gcuneh', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-08-12 10:56:17.150426'),
('u2lvscy9xjxgvqx9zls3nozdl83zv6b5', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-17 06:28:09.495724'),
('uyvb6aee1fd8cwz4htp3ox037q86gyxi', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-20 03:39:44.577782'),
('uyzr1mxyc51rppya3whp95lypodtzc8l', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-13 11:40:07.746612'),
('v3ytgr3yrzj9nc149c3ncmk32r0c12an', 'NDVjMTI0ZTVhYmIxZjFmOTU0OWI0Mzc2ZWNhOTViYjJiNzExOTVmODp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZjlkMThiMzY5MGY5YTAzZjkxNGE3M2EyNGNjMWE1MzQ0NjlmN2RmNCJ9', '2019-09-18 10:52:59.350262'),
('ytyux52myo07yem6db3swr67wfdkuamc', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-09-04 10:02:29.155900'),
('z9kv3rmc3btzsylryeik7hmhxpivho30', 'MjRhMGNkMGJkZWQxYmQwZjM5ZTAwOTk4OGI1MWYyMmQ4Nzk4MWQwMTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiRGphbmdvLmF1dGguRW1haWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiNGRiMTZlZDJhMDhiMGFiOWI3ZTFlMWVjNDRjNTQxOTRjMGZmMjZhMCJ9', '2019-07-16 06:23:23.679334'),
('ztbowvkhu3ez8qrma69vdjhxdj41aahv', 'NDlmMTQ1ZTJlMGYwY2E5ZTAyMzk0YTc0MDMzM2FiYmU3ZDIxYmJhNTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZm9jdXMuYXV0aC5FbWFpbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5OWRhNWUyODAxNDkxZTY3YWZmNGJiOTVmNjMzNjc1NzJhNWM3NDIyIn0=', '2019-08-23 11:07:17.544491');

-- --------------------------------------------------------

--
-- Структура таблицы `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `unit_id` int(11) NOT NULL COMMENT 'идентификатор компонента устройства',
  `type_id` int(11) NOT NULL COMMENT 'идентификатор типа сообщения',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'время возникновения события',
  `message` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `msg_types`
--

CREATE TABLE `msg_types` (
  `id` int(11) NOT NULL,
  `type` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `msg_types`
--

INSERT INTO `msg_types` (`id`, `type`) VALUES
(4, 'error'),
(1, 'event'),
(2, 'info'),
(5, 'status'),
(3, 'warning');

-- --------------------------------------------------------

--
-- Структура таблицы `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `roles`
--

INSERT INTO `roles` (`id`, `name`, `group_id`) VALUES
(1, 'Администратор', 1),
(2, 'Пользователь', 2);

-- --------------------------------------------------------

--
-- Структура таблицы `roles_group`
--

CREATE TABLE `roles_group` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `roles_group`
--

INSERT INTO `roles_group` (`id`, `name`) VALUES
(1, 'Управление'),
(2, 'Клиенты');

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_alert`
--

CREATE TABLE `snmp_alert` (
  `id` int(11) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `addr` varchar(255) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `is_read` smallint(6) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  `user_read` int(11) DEFAULT NULL,
  `history_id` int(11) DEFAULT NULL,
  `link_type` varchar(100) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `n_condition` varchar(100) DEFAULT NULL,
  `n_value` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp уведомления';

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_device`
--

CREATE TABLE `snmp_device` (
  `device_id` int(11) NOT NULL COMMENT ' ID малинки',
  `addr` varchar(255) NOT NULL COMMENT 'адрес узла ',
  `value_type` varchar(255) DEFAULT NULL COMMENT 'тип даных',
  `value` text COMMENT 'значение',
  `updated` datetime DEFAULT NULL COMMENT 'дата обновления',
  `mib_name` varchar(255) DEFAULT NULL COMMENT 'mib файл',
  `mib_syntax` text COMMENT 'mib тип',
  `mib_value` varchar(255) DEFAULT NULL COMMENT 'mib значение',
  `mib_node_name` text COMMENT 'mib имя узла',
  `mib_node_desc` text COMMENT 'mib описание узла'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp данные от устройств';

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_history`
--

CREATE TABLE `snmp_history` (
  `id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL COMMENT ' ID малинки',
  `addr` varchar(255) DEFAULT NULL COMMENT 'адрес узла ',
  `value` text COMMENT 'значение',
  `updated` datetime DEFAULT NULL COMMENT 'дата обновления',
  `mib_value` varchar(255) DEFAULT NULL COMMENT 'mib значение'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp история показаний устройств';

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_monitoring`
--

CREATE TABLE `snmp_monitoring` (
  `device_id` int(11) NOT NULL,
  `addr` varchar(255) NOT NULL,
  `interval` int(11) DEFAULT NULL COMMENT 'интервал запроса в минутах'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp устройства, которые необходимо отслеживать';

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_notifications`
--

CREATE TABLE `snmp_notifications` (
  `id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `addr` varchar(255) NOT NULL,
  `condition` varchar(100) NOT NULL,
  `value` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp услоявия отслеживания показаний';

-- --------------------------------------------------------

--
-- Структура таблицы `snmp_widgets`
--

CREATE TABLE `snmp_widgets` (
  `device_id` int(11) NOT NULL,
  `addr` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='snmp виджеты';

-- --------------------------------------------------------

--
-- Структура таблицы `status`
--

CREATE TABLE `status` (
  `id_delete` int(11) NOT NULL,
  `unit_id` int(11) NOT NULL COMMENT 'идентификатор компонента устройства',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'время изменения состояния',
  `state` varchar(8) NOT NULL DEFAULT '' COMMENT 'текущее состояние'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Структура таблицы `units`
--

CREATE TABLE `units` (
  `id` int(11) NOT NULL,
  `name` varchar(10) NOT NULL,
  `title` varchar(20) NOT NULL,
  `is_custom` tinyint(1) NOT NULL,
  `is_gpio` tinyint(1) NOT NULL,
  `comment` varchar(40) NOT NULL,
  `format` longtext NOT NULL,
  `family_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `units`
--

INSERT INTO `units` (`id`, `name`, `title`, `is_custom`, `is_gpio`, `comment`, `format`, `family_id`) VALUES
(1, 'self', 'Малинка', 0, 0, '', '{\n   \"title\": \"\",\n   \"type\": \"STRING\",\n    \"controls\": [],\n    \"chart\": \"\",\n    \"values\": [\n    {\n      \"value\": \"offline\",\n      \"title\": \"Оффлайн\",\n      \"class\": \"text-danger\"\n    },\n    {\n      \"value\": \"online\",\n      \"title\": \"Онлайн\",\n      \"class\": \"text-success\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"\",\n      \"class\": \"text-danger\"\n    }\n   ]\n}', 1),
(2, 'led1', 'Индикатор 1', 0, 1, '', '', 2),
(3, 'led2', 'Индикатор 2', 0, 1, '', '', 2),
(4, 'in1', 'Вход 1', 0, 1, '', '', 3),
(5, 'in2', 'Вход 2', 0, 1, '', '', 3),
(6, 'in3', 'Вход 3', 0, 1, '', '', 3),
(7, 'in4', 'Вход 4', 0, 1, '', '', 3),
(8, 'in5', 'Вход 5', 0, 1, '', '', 3),
(9, 'out1', 'Выход 1', 0, 1, '', '', 4),
(10, 'cnt1', 'Контроль 1', 1, 1, '', '{\n   \"title\": \"Контроль 1\",\n   \"type\": \"INTEGER\",\n   \"chart\": \"area\",\n   \"controls\": [\"toggle\"],\n   \"values\": [\n    {\n      \"value\": \"0\",\n      \"title\": \"Выключен\",\n      \"class\": \"bg-secondary text-white\"\n    },\n    {\n      \"value\": \"1\",\n      \"title\": \"Включен\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 4),
(11, 'out2', 'Выход 2', 0, 1, '', '', 4),
(12, 'cnt2', 'Контроль 2', 1, 1, '', '{\n   \"title\": \"Контроль 2\",\n   \"type\": \"INTEGER\",\n   \"chart\": \"area\",\n    \"controls\": [\"toggle\"],\n   \"values\": [\n    {\n      \"value\": \"0\",\n      \"title\": \"Выключен\",\n      \"class\": \"bg-secondary text-white\"\n    },\n    {\n      \"value\": \"1\",\n      \"title\": \"Включен\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 4),
(13, 'out3', 'Выход 3', 0, 1, '', '', 4),
(14, 'cnt3', 'Контроль 3', 1, 1, '', '{\n   \"title\": \"Контроль 3\",\n   \"type\": \"INTEGER\",\n   \"chart\": \"area\",\n    \"controls\": [\"toggle\"],\n   \"values\": [\n    {\n      \"value\": \"0\",\n      \"title\": \"Выключен\",\n      \"class\": \"bg-secondary text-white\"\n    },\n    {\n      \"value\": \"1\",\n      \"title\": \"Включен\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 4),
(15, 'out4', 'Выход 4', 0, 1, '', '', 4),
(16, 'cnt4', 'Контроль 4', 1, 1, '', '{\n   \"title\": \"Контроль 4\",\n   \"type\": \"INTEGER\",\n   \"chart\": \"area\",\n    \"controls\": [\"toggle\"],\n   \"values\": [\n    {\n      \"value\": \"0\",\n      \"title\": \"Выключен\",\n      \"class\": \"bg-secondary text-white\"\n    },\n    {\n      \"value\": \"1\",\n      \"title\": \"Включен\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 4),
(17, 'cpu', 'Датчик ЦПУ', 0, 0, 'Температура самой \"Малинки\"', '{\n   \"title\": \"Температура FocusPro\",\n   \"type\": \"FLOAT_RANGE\",\n   \"format\": \"{0:.2f} °C\",\n   \"chart\": \"spline\",\n    \"controls\": [],\n   \"values\": [\n    {\n      \"value\": \"-100..20\",\n      \"title\": \"\",\n      \"class\": \"bg-warning text-white\"\n    },\n    {\n      \"value\": \"20..60\",\n      \"title\": \"\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"60..200\",\n      \"title\": \"\",\n      \"class\": \"bg-danger text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 5),
(18, 'ext', 'Датчик внешней среды', 0, 0, 'Температура окружения \"Малинки\"', '{\n   \"title\": \"Температура внешней среды\",\n   \"type\": \"FLOAT_RANGE\",\n   \"format\": \"{0:.1f} °C\",\n   \"chart\": \"spline\",\n    \"controls\": [],\n   \"values\": [\n    {\n      \"value\": \"-100..0\",\n      \"title\": \"\",\n      \"class\": \"bg-warning text-white\"\n    },\n    {\n      \"value\": \"0..35\",\n      \"title\": \"\",\n      \"class\": \"bg-success text-white\"\n    },\n    {\n      \"value\": \"35..100\",\n      \"title\": \"\",\n      \"class\": \"bg-danger text-white\"\n    },\n    {\n      \"value\": \"иначе\",\n      \"title\": \"Неизвестно\",\n      \"class\": \"bg-light text-dark\"\n    }\n   ]\n}', 5),
(19, 'volt', 'Напряжение', 0, 1, 'Следит за исправностью напряжения', '', 6),
(20, 'block', 'Блокировка', 0, 1, 'Блокирует текущее состояние выходов', '', 6);

-- --------------------------------------------------------

--
-- Структура таблицы `units_family`
--

CREATE TABLE `units_family` (
  `id` int(11) NOT NULL,
  `name` varchar(10) NOT NULL,
  `title` varchar(20) NOT NULL,
  `comment` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `units_family`
--

INSERT INTO `units_family` (`id`, `name`, `title`, `comment`) VALUES
(1, 'self', 'Малинка', ''),
(2, 'leds', 'Индикаторы', 'Светодиодные индикаторы'),
(3, 'ins', 'Входы', ''),
(4, 'couts', 'Выходы', ''),
(5, 'temp', 'Температура', 'Датчики определения температуры'),
(6, 'misc', 'Разное', 'Компоненты без групповой принадлежности');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `app_menu`
--
ALTER TABLE `app_menu`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `auth_group_UN` (`code`);

--
-- Индексы таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Индексы таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Индексы таблицы `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `auth_user_clients_FK` (`client_id`),
  ADD KEY `auth_user_auth_group_FK` (`role_id`);

--
-- Индексы таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Индексы таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Индексы таблицы `broker_dispatcher_log`
--
ALTER TABLE `broker_dispatcher_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `broker_dispatcher_log_auth_user_FK` (`user_id`),
  ADD KEY `broker_dispatcher_log_devices_FK` (`device_id`);

--
-- Индексы таблицы `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `clients_UN` (`name`);

--
-- Индексы таблицы `commands`
--
ALTER TABLE `commands`
  ADD PRIMARY KEY (`id`),
  ADD KEY `commands_ibfk_1` (`device`);

--
-- Индексы таблицы `config`
--
ALTER TABLE `config`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `config_datatype_id_bdecfc26_fk_config_datatypes_id` (`datatype_id`),
  ADD KEY `config_group_id_32a30010_fk_config_groups_id` (`group_id`);

--
-- Индексы таблицы `config_datatypes`
--
ALTER TABLE `config_datatypes`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `config_groups`
--
ALTER TABLE `config_groups`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `devices_UN` (`name`),
  ADD KEY `devices_client_id_04804225_fk_clients_id` (`client_id`);

--
-- Индексы таблицы `devices_config`
--
ALTER TABLE `devices_config`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `devices_config_UN` (`device_id`,`unit_id`),
  ADD KEY `devices_config_unit_id_fcb9c4df_fk_units_id` (`unit_id`);

--
-- Индексы таблицы `device_routines`
--
ALTER TABLE `device_routines`
  ADD PRIMARY KEY (`id`),
  ADD KEY `NewTable_devices_FK` (`device_id`);

--
-- Индексы таблицы `device_routines_builtin`
--
ALTER TABLE `device_routines_builtin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `device_routines_builtin_UN` (`name`),
  ADD KEY `device_routines_builtin_devices_FK` (`device_id`);

--
-- Индексы таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Индексы таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`),
  ADD KEY `django_content_type_auth_group_FK` (`auth_group_id`);

--
-- Индексы таблицы `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Индексы таблицы `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `type_id` (`type_id`),
  ADD KEY `events_ibfk_1` (`unit_id`);

--
-- Индексы таблицы `msg_types`
--
ALTER TABLE `msg_types`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type` (`type`);

--
-- Индексы таблицы `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `roles_role_group_id_b525c387_fk_roles_group_id` (`group_id`);

--
-- Индексы таблицы `roles_group`
--
ALTER TABLE `roles_group`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `snmp_alert`
--
ALTER TABLE `snmp_alert`
  ADD PRIMARY KEY (`id`),
  ADD KEY `snmp_alert_snmp_device_FK` (`device_id`,`addr`),
  ADD KEY `snmp_alert_auth_user_FK` (`user_read`),
  ADD KEY `snmp_alert_snmp_history_FK` (`history_id`);

--
-- Индексы таблицы `snmp_device`
--
ALTER TABLE `snmp_device`
  ADD PRIMARY KEY (`device_id`,`addr`),
  ADD UNIQUE KEY `device_id` (`device_id`,`addr`);

--
-- Индексы таблицы `snmp_history`
--
ALTER TABLE `snmp_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `snmp_history_snmp_device_FK` (`device_id`,`addr`);

--
-- Индексы таблицы `snmp_monitoring`
--
ALTER TABLE `snmp_monitoring`
  ADD PRIMARY KEY (`device_id`,`addr`),
  ADD UNIQUE KEY `device_id` (`device_id`,`addr`);

--
-- Индексы таблицы `snmp_notifications`
--
ALTER TABLE `snmp_notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `snmp_notifications_snmp_device_FK` (`device_id`,`addr`);

--
-- Индексы таблицы `snmp_widgets`
--
ALTER TABLE `snmp_widgets`
  ADD PRIMARY KEY (`device_id`,`addr`);

--
-- Индексы таблицы `status`
--
ALTER TABLE `status`
  ADD PRIMARY KEY (`id_delete`),
  ADD UNIQUE KEY `unit_id` (`unit_id`);

--
-- Индексы таблицы `units`
--
ALTER TABLE `units`
  ADD PRIMARY KEY (`id`),
  ADD KEY `units_family_id_fdeddd7b_fk_units_family_id` (`family_id`);

--
-- Индексы таблицы `units_family`
--
ALTER TABLE `units_family`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `app_menu`
--
ALTER TABLE `app_menu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT для таблицы `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT для таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
--
-- AUTO_INCREMENT для таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=172;
--
-- AUTO_INCREMENT для таблицы `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
--
-- AUTO_INCREMENT для таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT для таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=183;
--
-- AUTO_INCREMENT для таблицы `broker_dispatcher_log`
--
ALTER TABLE `broker_dispatcher_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;
--
-- AUTO_INCREMENT для таблицы `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
--
-- AUTO_INCREMENT для таблицы `config`
--
ALTER TABLE `config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT для таблицы `config_datatypes`
--
ALTER TABLE `config_datatypes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT для таблицы `config_groups`
--
ALTER TABLE `config_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT для таблицы `devices`
--
ALTER TABLE `devices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;
--
-- AUTO_INCREMENT для таблицы `devices_config`
--
ALTER TABLE `devices_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1101;
--
-- AUTO_INCREMENT для таблицы `device_routines`
--
ALTER TABLE `device_routines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
--
-- AUTO_INCREMENT для таблицы `device_routines_builtin`
--
ALTER TABLE `device_routines_builtin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT для таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=172;
--
-- AUTO_INCREMENT для таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;
--
-- AUTO_INCREMENT для таблицы `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;
--
-- AUTO_INCREMENT для таблицы `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4618;
--
-- AUTO_INCREMENT для таблицы `msg_types`
--
ALTER TABLE `msg_types`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT для таблицы `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT для таблицы `roles_group`
--
ALTER TABLE `roles_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT для таблицы `snmp_alert`
--
ALTER TABLE `snmp_alert`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1042;
--
-- AUTO_INCREMENT для таблицы `snmp_history`
--
ALTER TABLE `snmp_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=375;
--
-- AUTO_INCREMENT для таблицы `snmp_notifications`
--
ALTER TABLE `snmp_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;
--
-- AUTO_INCREMENT для таблицы `status`
--
ALTER TABLE `status`
  MODIFY `id_delete` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4636;
--
-- AUTO_INCREMENT для таблицы `units`
--
ALTER TABLE `units`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
--
-- AUTO_INCREMENT для таблицы `units_family`
--
ALTER TABLE `units_family`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_user`
--
ALTER TABLE `auth_user`
  ADD CONSTRAINT `auth_user_auth_group_FK` FOREIGN KEY (`role_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_clients_FK` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `broker_dispatcher_log`
--
ALTER TABLE `broker_dispatcher_log`
  ADD CONSTRAINT `broker_dispatcher_log_auth_user_FK` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `broker_dispatcher_log_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `commands`
--
ALTER TABLE `commands`
  ADD CONSTRAINT `commands_ibfk_1` FOREIGN KEY (`device`) REFERENCES `devices` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `config`
--
ALTER TABLE `config`
  ADD CONSTRAINT `config_datatype_id_bdecfc26_fk_config_datatypes_id` FOREIGN KEY (`datatype_id`) REFERENCES `config_datatypes` (`id`),
  ADD CONSTRAINT `config_group_id_32a30010_fk_config_groups_id` FOREIGN KEY (`group_id`) REFERENCES `config_groups` (`id`);

--
-- Ограничения внешнего ключа таблицы `devices`
--
ALTER TABLE `devices`
  ADD CONSTRAINT `devices_client_id_04804225_fk_clients_id` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`);

--
-- Ограничения внешнего ключа таблицы `devices_config`
--
ALTER TABLE `devices_config`
  ADD CONSTRAINT `devices_config_device_id_cba51b4e_fk_devices_id` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`),
  ADD CONSTRAINT `devices_config_unit_id_fcb9c4df_fk_units_id` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`);

--
-- Ограничения внешнего ключа таблицы `device_routines`
--
ALTER TABLE `device_routines`
  ADD CONSTRAINT `NewTable_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `device_routines_builtin`
--
ALTER TABLE `device_routines_builtin`
  ADD CONSTRAINT `device_routines_builtin_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Ограничения внешнего ключа таблицы `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD CONSTRAINT `django_content_type_auth_group_FK` FOREIGN KEY (`auth_group_id`) REFERENCES `auth_group` (`id`);

--
-- Ограничения внешнего ключа таблицы `events`
--
ALTER TABLE `events`
  ADD CONSTRAINT `events_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `devices_config` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `events_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `msg_types` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `roles`
--
ALTER TABLE `roles`
  ADD CONSTRAINT `roles_role_group_id_b525c387_fk_roles_group_id` FOREIGN KEY (`group_id`) REFERENCES `roles_group` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_alert`
--
ALTER TABLE `snmp_alert`
  ADD CONSTRAINT `snmp_alert_auth_user_FK` FOREIGN KEY (`user_read`) REFERENCES `auth_user` (`id`),
  ADD CONSTRAINT `snmp_alert_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_device`
--
ALTER TABLE `snmp_device`
  ADD CONSTRAINT `snmp_device_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_history`
--
ALTER TABLE `snmp_history`
  ADD CONSTRAINT `snmp_history_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_monitoring`
--
ALTER TABLE `snmp_monitoring`
  ADD CONSTRAINT `snmp_monitoring_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_notifications`
--
ALTER TABLE `snmp_notifications`
  ADD CONSTRAINT `snmp_notifications_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `snmp_widgets`
--
ALTER TABLE `snmp_widgets`
  ADD CONSTRAINT `snmp_widgets_devices_FK` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`);

--
-- Ограничения внешнего ключа таблицы `status`
--
ALTER TABLE `status`
  ADD CONSTRAINT `status_ibfk_1` FOREIGN KEY (`unit_id`) REFERENCES `devices_config` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `units`
--
ALTER TABLE `units`
  ADD CONSTRAINT `units_family_id_fdeddd7b_fk_units_family_id` FOREIGN KEY (`family_id`) REFERENCES `units_family` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
