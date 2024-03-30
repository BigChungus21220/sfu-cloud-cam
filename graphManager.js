import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";
export default loadGraph

const dt = new Date();
dt.setHours(dt.getHours()-8);

const cameras = [
    {name:"Library Roof West", shorthand:"libWest", color:"steelblue"},
    {name:"Tower Road South", shorthand:"towSouth", color:"olivedrab"},
    {name:"Tower Road North", shorthand:"towNorth", color:"brown"},
    {name:"AQ Southeast", shorthand:"aqSouthEast", color:"chocolate"},
    {name:"SFU api", shorthand:"apiOutput", color:"RebeccaPurple"}
]

//set hours / minutes of a date
function setHourAndMinute(originalDate, hourMinuteString) {
    const [hour, minute] = hourMinuteString.split(':');
    const newDate = new Date(originalDate);
    newDate.setHours(hour);
    newDate.setMinutes(minute);
    return newDate;
}

//get data from csv file
async function getDataPoints(camera,day) {
    const filename = './output/' + camera.shorthand + '/' + day + '.csv';
    return await fetch(filename)
    .then((response) => response.text())
    .then((text) => {
        let arr = text.slice(0).split('\r\n').map(v => v.split(','))
        arr.pop(-1)
        for (let i = 0; i < arr.length; i++){
            arr[i] = {time:setHourAndMinute(dt,arr[i][0]),coverage:parseFloat(arr[i][1])}
        }
        return arr;
    });
}

//get data from all csv files
async function getCoverageData(day){
    let marks = [
        Plot.ruleY([0]),
        Plot.frame()
    ];

    const promises = cameras.map(camera => getDataPoints(camera,day)
        .then(points => Plot.lineY(points, { x: "time", y: "coverage", stroke: camera.color}))
    );

    await Promise.all(promises).then(result => {
        marks.push(...result);
    });

    return marks;
}

//set graph data
function loadGraph(day){
    getCoverageData(day).then((marks) => {
        const div = document.querySelector("#coverage_graph");
        div.innerHTML = '';
        div.append(Plot.plot({
            subtitle: "Cloud Coverage " + day,
            marginTop: 20,
            marginRight: 20,
            marginBottom: 30,
            marginLeft: 40,
            width: 1500,
            color: {legend: true},
            y: {grid: true, label: "Cloud Coverage"},
            marks
        }));
    })
}