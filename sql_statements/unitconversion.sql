insert into unit (unitName)
values ('l');
insert into unit (unitName)
values ('ml');
insert into unit (unitName)
values ('fl oz');
insert into unit (unitName)
values ('pt');
insert into unit (unitName)
values ('g');
insert into unit (unitName)
values ('mg');
insert into unit (unitName)
values ('kg');
insert into unit (unitName)
values ('oz');
insert into unit (unitName)
values ('lb');


insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('l', 'ml',1000);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('ml', 'l',0.001);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('l', 'fl oz',33,814);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('fl oz', 'l',0.0295735);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('l', 'pt',1.75975);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('pt', 'l',0.568261);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('ml', 'fl oz',0.033814);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('fl oz', 'ml',29.5735);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('ml', 'pt',0.00175975);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('pt', 'ml',568.261);
values ('fl oz', 'pt',0.0520421);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('pt', 'fl oz',19.2152);


insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('g', 'mg',1000);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('kg', 'g',1000);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('kg', 'oz',35.274);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('kg', 'lb',2.2);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('oz', 'g',28.35);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('lb', 'oz',16);
insert into unitconversion (sourceUnit, destinationUnit, ratio)
values ('lb', 'g',453.592);
