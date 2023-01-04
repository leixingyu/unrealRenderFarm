function createTable(list){
    // header row
    cols = ['uid', 'name', 'owner', 'worker', 'time_created', 'status', 'priority', 'time_estimate', 'progress'];
    var table = document.createElement("table");
    var tr = table.insertRow(-1);
    for (var i = 0; i < cols.length; i++) {
        // header th elements
        var theader = document.createElement("th");
        theader.innerHTML = cols[i];
        tr.appendChild(theader);
    }

    // data rows
    for (var i = 0; i < list.length; i++) {
        var trow = table.insertRow(-1);
        var uid = list[i]['uid'];

        for (var j = 0; j < cols.length; j++) {
            var cell = trow.insertCell(-1);
            cell.innerHTML = list[i][cols[j]];

            // add id tag to specific cells for ajax
            if (cols[j] == 'progress'){
                // container
                cell.innerHTML = '';
                cell.style.width = '200px';

                var container = document.createElement("div");
                cell.appendChild(container);
                container.setAttribute('class', 'progressContainer');

                // bar
                var bar = document.createElement("div");
                container.appendChild(bar);

                bar.setAttribute('class', 'progressBar');
                bar.setAttribute('id', uid + '_progress');

                bar.style.width = list[i]['progress'] + '%';
                bar.innerHTML = list[i]['progress'] + '%';

            }

            if (cols[j] == 'time_estimate'){
                cell.setAttribute('id', uid + '_estimate');
            }

            if (cols[j] == 'status'){
                cell.setAttribute('id', uid + '_status');
            }

        }
    }

    var el = document.getElementById("table");
    el.innerHTML = "";
    el.appendChild(table);
}



