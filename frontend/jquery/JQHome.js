
$(document).ready(function() {
	
	$("#trackingForm").submit(function() {
		var value = $("input[name=tracking]").val();
		
		$("#ajaxOutput").css("display", "none");
		$("#ajaxOutput").load("statusProgress.php?tracking="+value, function() {
			$("#ajaxOutput").slideDown("slow");
		});
		
		return false;
	});
	
});