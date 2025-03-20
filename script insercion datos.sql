INSERT INTO PRODUCTO (codBarra, descripcion, marca, stock, pCaja, pUnidad, pVenta, fechaRegistro)
VALUES 
('1234567890123', 'Cuaderno A4 100 hojas', 'Norma', 50, 12.50, 1.50, 2.00, GETDATE()), 
('9876543210987', 'Lapicero Azul BIC', 'BIC', 100, 5.00, 0.80, 1.00, GETDATE()), 
('4567891234567', 'Resaltador Amarillo Faber-Castell', 'Faber-Castell', 80, 7.50, 1.20, 1.50, GETDATE());
select * from PRODUCTO