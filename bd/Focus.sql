CREATE TABLE `rasp_config` (
  `rasp_id` 	int(11) NOT NULL 	COMMENT 'Индентификатор устройства, уникальный',
  `rasp_desc` 	varchar(45) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL 	COMMENT 'Описание',
  `host_ip` 	varchar(40) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL 	COMMENT 'IP адрес сервера',
  `live_time` 	int(11) NOT NULL 	COMMENT 'Интервал обмен собщениями, сек.',
  `web_pwd` 	varchar(20) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL 	COMMENT 'Пароль Web ',
  PRIMARY KEY (`rasp_id`),
  UNIQUE KEY `rasp_id_UNIQUE` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COLLATE=koi8r_bin COMMENT='Конфигурация устройств';

CREATE TABLE `ftemp` (
  `rasp_id` 	int(11) 	NOT NULL COMMENT 'Индентификатор устройства',
  `temp_num` 	int(11) 	NOT NULL COMMENT 'Номер датчика',
  `temp_desc` 	varchar(45) CHARACTER SET cp1251 COLLATE cp1251_general_ci DEFAULT NULL COMMENT 'Описание датчика',
  `temp_min` 	decimal(5,2) 	NOT NULL COMMENT 'Минимальное значение',
  `temp_max` 	decimal(5,2) 	NOT NULL COMMENT 'Максимальное значение',
  `temp_hold` 	decimal(5,2) 	NOT NULL COMMENT 'Номинальное значение ',
  `temp_int` 	int(11) 	NOT NULL COMMENT 'Интервал измерения, сек.',
  UNIQUE KEY `ftemp_unq` (`rasp_id`,`temp_num`),
  KEY `ftemp_fk_idx` (`rasp_id`),
  CONSTRAINT `ftemp_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='Датчики температуры';

CREATE TABLE `gpio` (
  `rasp_id` 	int(11) NOT NULL COMMENT 'Индентификатор устройства',
  `gpio_num` 	int(11) NOT NULL COMMENT 'Номер пина',
  `gpio_type` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT 'Тип пина (out / input / led / control /cnt)',
  `gpio_desc` 	varchar(45) DEFAULT NULL,
  `gpio_val` 	varchar(4) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL COMMENT 'Значение по умолчанию',
  UNIQUE KEY `gpio_unq` (`rasp_id`,`gpio_num`),
  KEY `gpio_fk_idx` (`rasp_id`),
  CONSTRAINT `gpio_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='ПИНы';

CREATE TABLE `inlive` (
  `inlive_id` 	int(11) 	NOT NULL AUTO_INCREMENT,
  `rasp_id` 	int(11) 	NOT NULL 	COMMENT 'Индентификатор устройства',
  `beg_time` 	datetime 	NOT NULL 	COMMENT 'Начало интервала',
  `end_time` 	datetime 	NOT NULL 	COMMENT 'Окончание интервала',
  `pause_time` 	int(11) 	DEFAULT NULL 	COMMENT 'Пауза отказа обмена после интервала, сек.',
  UNIQUE KEY `inlive_id_UNIQUE` (`inlive_id`),
  KEY `inlive_fk_idx` (`rasp_id`),
  CONSTRAINT `inlive_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=koi8r COMMENT='Интервалы непрерывного обмена';

CREATE TABLE `events` (
  `rasp_id` 	int(11) 	NOT NULL COMMENT 'Индентификатор устройства',
  `event_time` 	datetime 	NOT NULL COMMENT 'Время события',
  `event_type` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT 'Тип события (temp / pin)',
  `type_num` 	int(11) 	NOT NULL COMMENT 'Номер датчика / пина ',
  `event_val` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT 'Значение',
  KEY `event_fk_idx` (`rasp_id`),
  CONSTRAINT `event_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='События устройства';

CREATE TABLE `commands` (
  `rasp_id` 	int(11) 	NOT NULL 	COMMENT 'Индентификатор устройства',
  `com_time` 	datetime 	NOT NULL 	COMMENT 'Время формирования команды',
  `com_exec` 	datetime 	DEFAULT NULL 	COMMENT 'Время выполнения команды',
  `gpio_num` 	int(11) 	NOT NULL 	COMMENT 'Номер пина',
  `gpio_val` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT 'Значение (up / down)',
  `com_status` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT 'Статус команды (new / send / exec)',
  KEY `com_fk_idx` (`rasp_id`),
  CONSTRAINT `com_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='Команды для устройства';

DELIMITER $$
CREATE DEFINER=`FocusPro`@`localhost` FUNCTION `event_new`(rasp_in INT, 
							t_pin_type char(10), 
                                                        t_pin_num int, 
                                                        curr_val char(10)) 
RETURNS int(1)    DETERMINISTIC
BEGIN
DECLARE rasp_check INT; 
-- контроль идентификатора устройства 	
    select count(rasp_id) into rasp_check	
		from rasp_config
		where rasp_id = rasp_in;
    if rasp_check = 0 then
		RETURN 0;
    end if;
--  номера датчика температуры 
    if t_pin_type = 'temp' then
		select count(temp_num) into rasp_check	
			from ftemp
			where rasp_id = rasp_in and temp_num = t_pin_num;
		if rasp_check = 0 then
			RETURN 0;
		end if;
    end if;
--  номера ПИНа 
    if t_pin_type = 'gpio' then
		select count(gpio_num) into rasp_check	
			from gpio
			where rasp_id = rasp_in and gpio_num = t_pin_num;
		if rasp_check = 0 then
			RETURN 0;
		end if;
    end if;
-- запись события     
   insert into events (rasp_id, event_time, event_type, type_num, event_val)
		values (rasp_in, sysdate(), t_pin_type, t_pin_num, curr_val);
    RETURN 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`FocusPro`@`localhost` FUNCTION `inlive_new`(rasp_in INT) 
RETURNS int(1)    DETERMINISTIC
BEGIN
DECLARE rasp_check, rasp_live INT;
DECLARE	rasp_end, rasp_pas, curr_date datetime;
	Set curr_date = sysdate();
-- контроль идентификатора устройства 	
    Select live_time Into rasp_live	
		From rasp_config
		Where rasp_id = rasp_in;
    If rasp_live = 0 or rasp_live is null Then
		Return 0;
    End if;
    Select max(inlive_id) Into rasp_check
		From inlive 
		Where rasp_id = rasp_in
			and pause_time is null;
	If rasp_check = 0 or rasp_check is null Then 
		Insert Into inlive (rasp_id, beg_time, end_time, pause_time)
			Values (rasp_in, curr_date, curr_date, Null);
		Return 1;
    End if;
    Select end_time  Into rasp_end
		From inlive 
		Where inlive_id = rasp_check;
	If TIME_TO_SEC(curr_date) - TIME_TO_SEC(rasp_end) < rasp_live *2 Then
		Update inlive
			Set end_time = curr_date
		Where inlive_id = rasp_check;
	Else 
    	Update inlive
			Set pause_time = TIME_TO_SEC(curr_date) - TIME_TO_SEC(rasp_end)
		Where inlive_id = rasp_check;
		Insert Into inlive (rasp_id, beg_time, end_time, pause_time)
			Values (rasp_in, curr_date, curr_date, Null);
    End If;
	Return 1;
END$$
DELIMITER ;
