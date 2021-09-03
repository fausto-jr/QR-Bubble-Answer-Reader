<?php
include('libs/phpqrcode/qrlib.php'); 
include('libs/ez_sql_core.php');
include('libs/ez_sql_mysqli.php');
include('libs/config.php');

$gabarito_correto = "B,D,D,C,E,E,B,B,A,A,A,B,E,B,A,D,D,C,D,D,D,B,E,A,E,D,C,A,C,B,A,C,B,A,D,D,A,B,B,A";
$db = new ezSQL_mysqli(db_user,db_password,db_name,db_host);
	$pessoas = $db->get_results('SELECT * FROM answers');
	$cargos = $db->get_results("SELECT DISTINCT CARGO FROM answers");



	function compareAnswers($gabarito,$resposta){
	
	$espelho = explode(",",$gabarito);
	$resp_aluno = explode(",", $resposta);
	$arraysize_resp = count($resp_aluno);
	$arraysize_gaba = count($espelho);
	//echo $arraysize_resp."|".$arraysize_gaba;
	//$resultado = 0;
	$mat = 0;
	$lp = 0;
	$espec = 0;
	$atu = 0;

		//compareAnswers

		for($i=0; $i<$arraysize_resp; $i++){
			//echo $espelho[$i]."|".$resp_aluno[$i]."<br>";
			if ($espelho[$i] == $resp_aluno[$i] OR $i == 5)
			{
				if($i<=9){$mat++;}
				if($i>9 && $i<=19){$lp++;}
				if($i>19 && $i<=29){$espec++;}
				if($i>29){$atu++;}

				;
			}
		}
	$resultado = $mat+$lp+$espec+$atu;
	return array($mat,$lp,$espec,$atu,$resultado);
}
?>

<!DOCTYPE html>
<html>
	<head>
	<title>Gabarito</title>
	<link rel="icon" href="img/favicon.ico" type="image/png">
	<link rel="stylesheet" href="libs/css/bootstrap.min.css">
	
	</head>

	<body>
		<table class="table table-striped">
			<thead>
				<tr>
					<th>Numero</th>
					<th>Inscrição</th>
					<th>Nome</th>
					<th>CPF</th>
					<th>Cargo</th>
					<th>Matemática</th>
					<th>Português</th>
					<th>Específicas</th>
					<th>Atualidades</th>
					<th>Total</th>
				</tr>
			</thead>
			<tfoot>
				
			</tfoot>

			<tbody>
				<?php 
				$i=0;
				foreach ($pessoas as $pessoa) {
					$inscri = $pessoa->NUMERO;
					$nome  = $pessoa->NOME;
					$cpf = $pessoa->CPF;
					$cargo = $pessoa->CARGO;
					$id = $pessoa->id;

					$gabarito = $db->get_var("SELECT answers FROM gabarito WHERE id = $id");
					//$db->debug();
					if($gabarito != NULL){
						$i += 1;
						$pontuacao = compareAnswers($gabarito_correto,$gabarito);
						echo "<tr><td>$i</td><td>$inscri</td><td>".utf8_encode($nome)."</td><td>".$cpf."</td><td>".$cargo."</td><td>".$pontuacao[0]."</td><td>".$pontuacao[1]."</td>
						<td>".$pontuacao[2]."</td><td>".$pontuacao[3]."</td><td>".$pontuacao[4]."</td></tr>";
					}

				}



				?>
			</tbody>
		</table>


	</body>