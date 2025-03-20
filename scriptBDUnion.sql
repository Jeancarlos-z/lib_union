
CREATE TABLE DETALLE_VENTA
( 
	idVenta              int  NOT NULL ,
	idProducto           int  NOT NULL ,
	cantidad             int  NOT NULL check(cantidad >0),
	pUnidad              decimal(10,2)  NOT NULL check(pUnidad >=0)
)
go



ALTER TABLE DETALLE_VENTA
	ADD CONSTRAINT XPKDETALLE_VENTA PRIMARY KEY  CLUSTERED (idVenta ASC,idProducto ASC)
go



CREATE TABLE PRODUCTO
( 
	idProducto           int IDENTITY ( 1,1 ) ,
	codBarra             varchar(20)  NOT NULL ,
	descripcion          varchar(100)  NOT NULL ,
	imagen			     varchar(150)  NOT NULL ,
	marca                varchar(50)  NOT NULL ,
	stock                int  NULL check(stock >=0),
	pCaja                decimal(10,2)  NOT NULL check(pCaja >=0),
	pUnidad              decimal(10,2)  NOT NULL check(pUnidad >=0),
	pVenta               decimal(10,2)  NOT NULL check(pVenta >=0),
	fechaRegistro        datetime2(0)  NOT NULL 
)
go



ALTER TABLE PRODUCTO
	ADD CONSTRAINT XPKPRODUCTOS PRIMARY KEY  CLUSTERED (idProducto ASC)
go



CREATE TABLE VENTA
( 
	idVenta              int IDENTITY ( 1,1 ) ,
	fechaVenta           datetime2(0)  NOT NULL 
)
go



ALTER TABLE VENTA
	ADD CONSTRAINT XPKVENTA PRIMARY KEY  CLUSTERED (idVenta ASC)
go




ALTER TABLE DETALLE_VENTA
	ADD CONSTRAINT R_1 FOREIGN KEY (idVenta) REFERENCES VENTA(idVenta)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go




ALTER TABLE DETALLE_VENTA
	ADD CONSTRAINT R_3 FOREIGN KEY (idProducto) REFERENCES PRODUCTO(idProducto)
		ON DELETE NO ACTION
		ON UPDATE NO ACTION
go
