CREATE TABLE `racism_word_frequency`(
  `id` INT NOT NULL AUTO_INCREMENT,
  `word` VARCHAR(20) NOT NULL,
  `frequency` INT NOT NULL DEFAULT 0,
  PRIMARY KEY(`id`)
)DEFAULT CHARSET = 'UTF8';

CREATE TABLE `racism_word_frequency_india`(
  `id` INT NOT NULL AUTO_INCREMENT,
  `word` VARCHAR(20) NOT NULL,
  `frequency` INT NOT NULL DEFAULT 0,
  PRIMARY KEY(`id`)
)DEFAULT CHARSET = 'UTF8';