base_chart = """
<script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
%s
      }
    </script>
"""

annotadtime_chart = """
 <script type='text/javascript'>
      google.load('visualization', '1', {'packages':['annotatedtimeline']});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
%s
    }
    </script>
"""

div = """<div id="%s"></div>"""

annotatedtime_div = """<div id="%s" style='width: %ipx;height: %ipx;'></div>"""
