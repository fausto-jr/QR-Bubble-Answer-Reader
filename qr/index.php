<?php
include('libs/phpqrcode/qrlib.php'); 
include('libs/ez_sql_core.php');
include('libs/ez_sql_mysqli.php');
include('libs/config.php');


$tempDir = 'temp/'; 
	


$db = new ezSQL_mysqli(db_user,db_password,db_name,db_host);
	$pessoas = $db->get_results('SELECT * FROM answers WHERE CARGO = "PROF. LIC. EM PEDAGOGIA 30H - TEMP"');
	$cargos = $db->get_results("SELECT DISTINCT CARGO FROM answers");
	
	foreach ($cargos as $cargo){
		//echo $cargo->CARGO."<br>";
		/* 
PROF. LIC. EM PEDAGOGIA 30H - TEMP
PROF. LIC. LETRAS 30H - TEMP
PROF. LIC. MATEMATICA 30H - TEMP
PROF. LIC. CIENCIAS 30H - TEMP
PROF. LIC. EM ED. FISICA 30H - TEMP
PROF. LIC. GEOGRAFIA 30H - TEMP
PROF. LIC. HISTORIA 30H - TEMP
		*/
	}
?>
<!DOCTYPE html>
<html lang="en-US">
	<head>
	<title>Gabarito</title>
	<link rel="icon" href="img/favicon.ico" type="image/png">
	<link rel="stylesheet" href="libs/css/bootstrap.min.css">
	<link rel="stylesheet" href="libs/style.css">
	</head>
	<body onload="startTime()">
			
				<?php 

foreach ($pessoas as $pessoa){

	$random1 = substr(number_format(time() * rand(),0,'',''),0,10); 
	$body =  $pessoa->id.','.$pessoa->NUMERO;
	$filename = $tempDir.$body.$random1.'.png';
	QRcode::png($body, $filename, QR_ECLEVEL_L, 5);
	 echo '<div class="input-field">
				<div class="qr-field"><img src="'. @$filename.'" class="absolute"><br>'; 

	 echo '<div style="float: left; margin-left: 40%;"><h6>NOME: '.utf8_encode($pessoa->NOME).' </h6> <h6>CPF: '.$pessoa->CPF.' INSC.: '.$pessoa->NUMERO.' ID: '.$pessoa->id.'</h6><h6>CARGO: '.$pessoa->CARGO.'</h6><h6>______________________________________<br>Assinatura do Candidato</h6></div>
				</div>
				<div class="letras">
				<img src="img/letras40B.png" class="relative"/>
				</div>
				
			</div>
			<div class="pagebreak"> </div>';
	}
?>
				

				
		
			
			<?php
			
			if (!isset($filename))
				$filename= "asd";
			?>
			
			
		
	</body>
	
</html>