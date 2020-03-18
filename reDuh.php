<?php
	error_reporting(E_ALL);
	ini_set('display_errors', true);
	ini_set('html_errors', false);


	function errorlog($log)
	{
		$DEBUG=FALSE;

		if($DEBUG)
		{
			error_log($log);
		}
	}

	function check_sock_error($area)
	{
		$err = socket_last_error();

		if($err>0)
		{
			errorlog("CHECK_SOCK_ERROR(".$area."): ".socket_strerror(socket_last_error()));
			socket_clear_error();
		}
	}

	function handle_exceptions(&$es)
	{
		foreach($es as $s)
		{
			errorlog("BACKEND: Got exception on socket ".$s);
		}
	}

	function send_command($port, $method, $data, $id)
	{
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL,"http://127.0.0.1:".$port."/".$id);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		switch ($method) {
			case 'GET':
				break;
			case 'POST':
				curl_setopt($ch, CURLOPT_POST, 1);
				break;
			default:
				curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
				break;
		}
		if ($method == "PUT" || $method == "POST") {
			curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
		}

		$ret = curl_exec($ch);

		return $ret;
	}


	set_time_limit(0);

	if(array_key_exists('action',$_REQUEST))
	{
		$action = $_REQUEST['action'];

		if($action == 'checkPort')
		{
			echo "Success\n";

		}
		else if($_REQUEST['action'] == 'startReDuh')
		{
			$cmd = '/usr/bin/python '.dirname(__FILE__).'/reDuh.py -p '.$_REQUEST['servicePort'];
			exec($cmd);
			print_r($cmd);
		}
		else if($_REQUEST['action'] == 'killReDuh')
		{
			$port = $_REQUEST['servicePort'];

			send_command($port, "POST", array("die" => 1), "");

			echo "Success\n";
		}
		else if($_REQUEST['action'] == 'getData')
		{
			sleep(1);
			$port = $_REQUEST['servicePort'];

			$response = send_command($port, "GET", "", "");
			$response = (strlen($response) > 0) ? $response : "[NO_NEW_DATA]";
			header("DEBUG: " . strlen($response));

			echo $response."\n";
		}
		else if($_REQUEST['action'] == 'createSocket')
		{
			$port = $_REQUEST['servicePort'];
			$socketNumber = $_REQUEST['socketNumber'];
			$targetHost = $_REQUEST['targetHost'];
			$targetPort = $_REQUEST['targetPort'];

			send_command($port, "POST", array("host" => $targetHost, "port" => $targetPort), $socketNumber);

			echo "Success\n";
		}
		else if($_REQUEST['action'] == "newData")
		{
			$port = $_REQUEST['servicePort'];
			$socketNumber = $_REQUEST['socketNumber'];
			$targetHost = $_REQUEST['targetHost'];
			$targetPort = $_REQUEST['targetPort'];
            $sequenceNumber = $_REQUEST['sequenceNumber'];
			$data = $_REQUEST['data'];

			send_command($port, "PUT", array("data" => $data), $socketNumber);

			echo "Success\n";
		}
		else
		{
			errorlog("Unknown action '".$_REQUEST['action']."'");
			echo "Unknown action '".$_REQUEST['action']."'\n";
		}
	} 
	else
	{
		echo "Unknown request to ReDuh!\n";
	}
?>
