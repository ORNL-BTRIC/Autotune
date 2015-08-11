$(document).ready(function() {
	var button = $("input[value=Download]");
	//check all
	$("#check").click(function() {
		$("input[type=checkbox]").prop("checked", true);
		button.removeAttr("disabled");
		//console.log("enabled");
		
	});
	
	//uncheck all
	$("#uncheck").click(function() {
		$("input[type=checkbox]").prop("checked", false);
		button.attr("disabled", "disabled");
		//console.log("disabled");
	});
	
	//disable button if none are checked
	var checkboxes = $("input[type=checkbox]");
	checkboxes.change(function() {
		var noneChecked = true;
		checkboxes.each(function() {
			if($(this).prop("checked")) {
				noneChecked = false;
			}
		});
		
		if(noneChecked) {
			button.attr("disabled", "disabled");
			//console.log("disabled");
		}
		else {
			button.removeAttr("disabled");
			//console.log("enabled");
		}
	});
	
	//accordian
	var activeBlock;
	if($(".resumeOption").css("display") == 'none') {
		activeBlock = 0;
	}
	else if($(".stopOption").css("display") == 'none') {
		activeBlock = 1;
	}
	$("#accordion").accordion({ 
		collapsible: true,
		active: activeBlock,
		heightStyle: "content"
	});
	
	var value = $("#modelNum").text();
	
	// update the status of the order
	$("#ajaxStatus").load("statusUpdate.php?trackingId="+value);
	
	
	$("#stop").click(function() {
		$( "#dialog-modal" ).dialog("open");
		$("#stopDialog").show();
		
		var url = encodeURIComponent("http://yourdomain.com/autotune/service/service.php?tracking="+value + "&terminate=1");
		$("#ajax").load("proxy.php?url=" + url);
		
		$(".resumeOption").show();
		$(".stopOption").hide();
		$("#accordion" ).accordion( "destroy");
		$("#accordion").accordion({ 
			collapsible: true, 
			active: false
		});
	});
	
	$("#resume").click(function() {
		$( "#dialog-modal" ).dialog("open");
		$("#resumeDialog").show();
		
		var url = encodeURIComponent("http://yourdomain.com/autotune/service/service.php?tracking="+value+"&terminate=0");
		$("#ajax").load("proxy.php?url=" + url);
		$("#ajax").show();
		
	
		$(".stopOption").show();
		$(".resumeOption").hide();
		$("#accordion" ).accordion( "destroy");
		$("#accordion").accordion({ 
			collapsible: true, 
			active: false
		});
		$("#ajaxStatus").load("statusUpdate.php?trackingId="+value);	
	});
	
	$("#retune").click(function() {
		$( "#dialog-modal" ).dialog("open");
		$("#retuneDialog").show();
		
		var url = encodeURIComponent("http://yourdomain.com/autotune/service/service.php?tracking="+value+"&retune=1");
	
		console.log(url);
		$.post("proxy.php?url=" + url, function(data) {
					xmlDoc = $.parseXML(data),
					$xml = $(xmlDoc),
					$tracking = $xml.find("tracking");
					$position = $xml.find("position");
					$("#ajax").html("New Model Number: " + $tracking.text() + '<BR>');
					$("#ajax").append("Position: " + $position.text() + '<BR>');
								
		});
	
	});
	
	//modal dialog
	$( "#dialog-modal" ).dialog({
		autoOpen: false,
		modal: true,
		buttons: {
			Ok: function() {
				$(this).dialog("close");
			}
		},
		close: function() {
			$("[id$=Dialog]").hide();
		}
    });
	
	//
	
	$("[id$=Dialog]").hide();
	
});