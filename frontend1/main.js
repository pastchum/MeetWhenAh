var selectedList = [];


function getURLParams() {
    const params = new URLSearchParams(window.location.search);

    let startDate = new moment(params.get('startDate', 'YYYY-mm-dd'));
    let endDate = new moment(params.get('endDate', 'YYYY-mm-dd'));
    let eventID = params.get('eventID');
    let eventName = params.get('eventName');
    data = {
        startDate: startDate,
        endDate: endDate,
        eventID: eventID,
        eventName: eventName
    }
    return data;
  }

function main() {
    
    let urlParams = getURLParams()
    let days = urlParams.endDate.diff(urlParams.startDate, 'days')

    const table = document.getElementById('table');

    var date = moment()
    date.startOf('day')
    row = document.createElement('tr');
    for (let hours = 0; hours < 48; hours++) {
        header = document.createElement('th');
        header.textContent = date.format('HH:mm');
        row.appendChild(header);
        date.add(30, 'minutes');
    }
    table.appendChild(row);

    for (let i = 0; i < days; i++) {
        header = document.createElement('th');
        header.textContent = urlParams.startDate.add(1, 'days').format('DD-MMMM-YYYY');

        row = document.createElement('tr');
        var date = urlParams.startDate.add(1, 'days')
        date.startOf('day')
        for (let hours = 0; hours < 48; hours++) {
            cell = document.createElement('td');
            //cell.setAttribute("data-date-time", date);
            row.appendChild(cell);
            date.add(30, 'minutes');
        }
        table.append(header);
        table.appendChild(row);
    }
        
    const heading = document.getElementById('title');
    const dateRange = document.getElementById('dateRange');
    heading.textContent = urlParams.eventName;
    dateRange.textContent = urlParams.startDate.format('DD-MMMM-YYYY') + " - " + urlParams.endDate.format('DD-MMMM-YYYY');


    //this thing inverts the whole table
    $("table").each(function() {
        var $this = $(this);
        var newrows = [];
        $this.find("tr").each(function() {
          var i = 0;
          $(this).find("td,th").each(function() {
            i++;
            if (newrows[i] === undefined) {
              newrows[i] = $("<tr></tr>");
            }
            newrows[i].append($(this));
          });
        });
        $this.find("tr").remove();
        $.each(newrows, function() {
          $this.append(this);
        });
      });

}
var table = $("#table");    
var isMouseDown = false;
var startRowIndex = null;
var startCellIndex = null;
//for some godforsaken reason this requires a timeout. dont ask me why
setTimeout(() => {
    table.find("td").mousedown(function (e) {
        isMouseDown = true;
        var cell = $(this);
    
        //table.find(".selected").removeClass("selected"); // deselect everything
        
        if (e.shiftKey) {
            selectTo(cell);                
        } else {
            cell.addClass("selected");
            //selectedList.push(cell[0].getAttribute('data-date-time'));
            startCellIndex = cell.index();
            startRowIndex = cell.parent().index()-1;
        }
        
        return false; // prevent text selection
    })
    .mouseover(function () {
        if (!isMouseDown) return;
        //table.find(".selected").removeClass("selected"); // deselect everything
        selectTo($(this));
    })
    .bind("selectstart", function () {
        return false;
    });
    
    $(document).mouseup(function () {
        isMouseDown = false;
    });
},100);

function resetHours() {
    table.find(".selected").removeClass("selected"); // deselect everything
    selectedList = [];
    return;
}


function selectTo(cell) {
    
    var row = cell.parent();    
    var cellIndex = cell.index()-1;
    var rowIndex = row.index();
    
    var rowStart, rowEnd, cellStart, cellEnd;
    
    if (rowIndex < startRowIndex) {
        rowStart = rowIndex;
        rowEnd = startRowIndex;
    } else {
        rowStart = startRowIndex;
        rowEnd = rowIndex;
    }
    
    if (cellIndex < startCellIndex) {
        cellStart = cellIndex;
        cellEnd = startCellIndex;
    } else {
        cellStart = startCellIndex;
        cellEnd = cellIndex;
    }        
    
    for (var i = rowStart; i <= rowEnd; i++) {
        var rowCells = table.find("tr").eq(i).find("td");
        for (var j = cellStart; j <= cellEnd; j++) {
            var cell = rowCells.eq(j)
            cell.addClass("selected");
            
            //console.log(cell.get(0).getAttribute('data-date-time'));
        }        
    }
}

function parseAvailability() {
    console.log(selectedList);
}


function senddata() {
    data = {
        hours_available: hours_available,
        event_id: event_id
    }
    console.log(data);
    Telegram.WebApp.sendData(data);
}

    

