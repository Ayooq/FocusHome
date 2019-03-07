CREATE TABLE `rasp_config` (
  `rasp_id` 	int(11) NOT NULL 	COMMENT '�������������� ����������, ����������',
  `rasp_desc` 	varchar(45) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL 	COMMENT '��������',
  `host_ip` 	varchar(40) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL 	COMMENT 'IP ����� �������',
  `live_time` 	int(11) NOT NULL 	COMMENT '�������� ����� ����������, ���.',
  `web_pwd` 	varchar(20) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL 	COMMENT '������ Web ',
  PRIMARY KEY (`rasp_id`),
  UNIQUE KEY `rasp_id_UNIQUE` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COLLATE=koi8r_bin COMMENT='������������ ���������';

CREATE TABLE `ftemp` (
  `rasp_id` 	int(11) 	NOT NULL COMMENT '�������������� ����������',
  `temp_num` 	int(11) 	NOT NULL COMMENT '����� �������',
  `temp_desc` 	varchar(45) CHARACTER SET cp1251 COLLATE cp1251_general_ci DEFAULT NULL COMMENT '�������� �������',
  `temp_min` 	decimal(5,2) 	NOT NULL COMMENT '����������� ��������',
  `temp_max` 	decimal(5,2) 	NOT NULL COMMENT '������������ ��������',
  `temp_hold` 	decimal(5,2) 	NOT NULL COMMENT '����������� �������� ',
  `temp_int` 	int(11) 	NOT NULL COMMENT '�������� ���������, ���.',
  UNIQUE KEY `ftemp_unq` (`rasp_id`,`temp_num`),
  KEY `ftemp_fk_idx` (`rasp_id`),
  CONSTRAINT `ftemp_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='������� �����������';

CREATE TABLE `gpio` (
  `rasp_id` 	int(11) NOT NULL COMMENT '�������������� ����������',
  `gpio_num` 	int(11) NOT NULL COMMENT '����� ����',
  `gpio_type` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT '��� ���� (out / input / led / control /cnt)',
  `gpio_desc` 	varchar(45) DEFAULT NULL,
  `gpio_val` 	varchar(4) CHARACTER SET koi8r COLLATE koi8r_general_ci DEFAULT NULL COMMENT '�������� �� ���������',
  UNIQUE KEY `gpio_unq` (`rasp_id`,`gpio_num`),
  KEY `gpio_fk_idx` (`rasp_id`),
  CONSTRAINT `gpio_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='����';

CREATE TABLE `inlive` (
  `inlive_id` 	int(11) 	NOT NULL AUTO_INCREMENT,
  `rasp_id` 	int(11) 	NOT NULL 	COMMENT '�������������� ����������',
  `beg_time` 	datetime 	NOT NULL 	COMMENT '������ ���������',
  `end_time` 	datetime 	NOT NULL 	COMMENT '��������� ���������',
  `pause_time` 	int(11) 	DEFAULT NULL 	COMMENT '����� ������ ������ ����� ���������, ���.',
  UNIQUE KEY `inlive_id_UNIQUE` (`inlive_id`),
  KEY `inlive_fk_idx` (`rasp_id`),
  CONSTRAINT `inlive_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=koi8r COMMENT='��������� ������������ ������';

CREATE TABLE `events` (
  `rasp_id` 	int(11) 	NOT NULL COMMENT '�������������� ����������',
  `event_time` 	datetime 	NOT NULL COMMENT '����� �������',
  `event_type` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT '��� ������� (temp / pin)',
  `type_num` 	int(11) 	NOT NULL COMMENT '����� ������� / ���� ',
  `event_val` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT '��������',
  KEY `event_fk_idx` (`rasp_id`),
  CONSTRAINT `event_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='������� ����������';

CREATE TABLE `commands` (
  `rasp_id` 	int(11) 	NOT NULL 	COMMENT '�������������� ����������',
  `com_time` 	datetime 	NOT NULL 	COMMENT '����� ������������ �������',
  `com_exec` 	datetime 	DEFAULT NULL 	COMMENT '����� ���������� �������',
  `gpio_num` 	int(11) 	NOT NULL 	COMMENT '����� ����',
  `gpio_val` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT '�������� (up / down)',
  `com_status` 	varchar(10) CHARACTER SET koi8r COLLATE koi8r_general_ci NOT NULL COMMENT '������ ������� (new / send / exec)',
  KEY `com_fk_idx` (`rasp_id`),
  CONSTRAINT `com_fk` FOREIGN KEY (`rasp_id`) REFERENCES `rasp_config` (`rasp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=koi8r COMMENT='������� ��� ����������';

DELIMITER $$
CREATE DEFINER=`FocusPro`@`localhost` FUNCTION `event_new`(rasp_in INT, 
							t_pin_type char(10), 
                                                        t_pin_num int, 
                                                        curr_val char(10)) 
RETURNS int(1)    DETERMINISTIC
BEGIN
DECLARE rasp_check INT; 
-- �������� �������������� ���������� 	
    select count(rasp_id) into rasp_check	
		from rasp_config
		where rasp_id = rasp_in;
    if rasp_check = 0 then
		RETURN 0;
    end if;
--  ������ ������� ����������� 
    if t_pin_type = 'temp' then
		select count(temp_num) into rasp_check	
			from ftemp
			where rasp_id = rasp_in and temp_num = t_pin_num;
		if rasp_check = 0 then
			RETURN 0;
		end if;
    end if;
--  ������ ���� 
    if t_pin_type = 'gpio' then
		select count(gpio_num) into rasp_check	
			from gpio
			where rasp_id = rasp_in and gpio_num = t_pin_num;
		if rasp_check = 0 then
			RETURN 0;
		end if;
    end if;
-- ������ �������     
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
-- �������� �������������� ���������� 	
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
