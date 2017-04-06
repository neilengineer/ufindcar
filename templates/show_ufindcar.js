Array.max = function( array ){
    return Math.max.apply( Math, array );
};
Array.min = function( array ){
    return Math.min.apply( Math, array );
};
function isInArray(value, array) {
    return array.indexOf(value) > -1;
}
function change_bg_color() {
    var color = d3.scale.category20();
    document.body.style.background = color(Math.random()*10);
    document.body.style.opacity = "0.3";
}
/*
function CreateNode(nodeId,label,className,nodeType)
{   
  var node = d3.select("svg").append('g');

  node.append("circle")
   .attr("cx", CalculateX(nodeType))
   .attr("cy", CalculateY(nodeType))
   .attr("r",40)
   .style("fill","none")
   .style("stroke","#ccc")
   .attr("nodeId",nodeId)
   .attr("class",className);

   node.append("text")
    .attr("x", CalculateX(nodeType))    
    .attr("y", CalculateY(nodeType))
    .attr("text-anchor", "middle")  
    .style("font-size", "14px")
    .attr('fill','#cccccc')
    .text(label);

    return node;
}
*/

var drag = d3.behavior.drag()
            .origin(function() {
                return { x: parseInt(d3.select(this).style("left")),
                         y: parseInt(d3.select(this).style("top")) };
            })
            .on("drag", function() {
                d3.select(this)
                    .style("left", d3.event.x + "px")   //for div left,top unit is 'px', for svg not needed
                    .style("top", d3.event.y + "px");
            });

function create_bubble_chart(data_json_array) {
    var percent = 0.8
    var w = window.innerWidth*percent;
    var h = window.innerHeight*percent;
    var wh_ratio = w/h;
    var xpad = w/15;
    var xpad_right = xpad;
    var ypad = h/20;
    var ypad_bottom = ypad;
    var radius = (xpad+xpad_right)/(15);
    var min_x = max_x = 0;
    var min_y = max_y = 0;
    var dataset = data_json_array;

    var tmp_array_x = []; 
    var tmp_array_y = [];
    for (var i = 0; i < dataset.length; i++) {
        tmp_array_x[i] = dataset[i].mileage;
        tmp_array_y[i] = dataset[i].price;
    }
    min_x = Array.min(tmp_array_x);
    max_x = Array.max(tmp_array_x);
    min_y = Array.min(tmp_array_y);
    max_y = Array.max(tmp_array_y);
//    console.log(min_x,max_x,min_y,max_y);
    var xScale = d3.scale.linear()
                 .domain([min_x, max_x])
                 .range([xpad, w-xpad-radius-xpad_right]);
    var yScale = d3.scale.linear()
                 .domain([min_y, max_y])
                 .range([h-ypad-radius-ypad_bottom, ypad]);
    var color = d3.scale.category20();
    var xAxis = d3.svg.axis().scale(xScale)
        .orient("bottom").ticks(5);
    var yAxis = d3.svg.axis().scale(yScale)
        .orient("left").ticks(5);
    var div = d3.select("body")
        .append("div")  // declare the tooltip div 
        .attr("class", "tooltip")              // apply the 'tooltip' class
        .call(drag)
        .style("opacity", 0);                  // set the opacity to nil

    var svg = d3.select("#ufindcar_show")
                .append("svg")
                .attr("width", w)
                .attr("height", h)
                .attr("viewBox", "0 0 " + w +' '+ h)
                .attr("preserveAspectRatio", "xMidYMid meet");

    //append circles to svg/g node
    svg.selectAll("circle")
       .data(dataset)
       .enter()
       .append("g")
       .append("circle")
       .attr("cx", function (d, i) { return xScale(d.mileage); })
       .attr("cy", function (d, i) { return yScale(d.price); })
       .attr("r", radius)
       .attr("fill",function(d,i){return color(i);})
       .on("mouseover", function(d) {      
            div.transition()
                .duration(10)
                .style("opacity", .9);  
            div.html(
                '<a target="_blank" href=' + d.url + '>'+ d.entry_title + '</a><br>' +
                'Mileage: ' + d.mileage + ' miles<br>' +
                'Price: ' + d.price + ' USD<br>' +
                'Place: ' + d.place + '<br>' +
                'Title Status: ' + d.title_status + '<br>' +
                'Available Date: ' + d.date.split("T")[0]
                )
                .style("left", (d3.event.pageX + 10) + "px")
                .style("top", (d3.event.pageY - 30) + "px");
        });

    //append text to svg/g node
    var num_red_hearts = 10;
    svg.selectAll("g")
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-family','FontAwesome')
        .attr('font-size', radius/2+'px')
        .attr("x", function (d, i) { return xScale(d.mileage); })
        .attr("y", function (d, i) { return yScale(d.price); })
        .attr("fill", function (d, i) { if(i < num_red_hearts) {return 'red';} })
        .text(function (d,i) {
            if(i < num_red_hearts){
                //top 10 cars, use red heart, :)
                return '\uf004';
            }else{
                return '\uf1b9';
            }
        })
       .on("mouseover", function(d) {
            div.transition()
                .duration(10)
                .style("opacity", .9);
            div.html(
                '<a target="_blank" href=' + d.url + '>'+ d.entry_title + '</a><br>' +
                'Mileage: ' + d.mileage + ' miles<br>' +
                'Price: ' + d.price + ' USD<br>' +
                'Place: ' + d.place + '<br>' +
                'Title Status: ' + d.title_status + '<br>' +
                'Available Date: ' + d.date.split("T")[0]
                )
                .style("left", (d3.event.pageX + 10) + "px")
                .style("top", (d3.event.pageY - 30) + "px");
        });

    var all_node = svg.selectAll("g");
/*
        .on("mouseout", function(d){
            div.transition()
                .duration(100)
                .style("opacity", 0); }
        );
*/
    svg.append("g") 
        .attr("class", "axis")
        .attr("transform", "translate(0," + (h-radius-ypad_bottom) + ")")
        .call(xAxis);
    svg.append("g") 
        .attr("class", "axis")
        .attr("transform", "translate("+ (xpad-radius-2) + ",0)")
        .call(yAxis);
    //axis labels
    svg.append("text")
       .text("Mileage(miles)")
       .attr("x", w-xpad-xpad_right-radius-50)
       .attr("y", h-5)
       .attr("font-family", "sans-serif")
       .attr("font-size", "13px");
    svg.append("text")
       .text("Price(USD)")
       .attr("x", xpad/15)
       .attr("y", ypad/1.5)
       .attr("font-family", "sans-serif")
       .attr("font-size", "13px");

/*  filter select options */
    var FILTER_MAKE = 0;
    var FILTER_YEAR = 1;
    var FILTER_PRICE = 2;
    var FILTER_MILEAGE = 3;
    var FILTER_TITLE = 4;
    var FILTER_TYPE = 5;
    var FILTER_AREA = 6;
    var sel_arr_make = {"all makes":'all',"ford":"ford","toyota":"toyota","honda":"honda","nissan":"nissan","chevrolet":"chevrolet","hyundai":"hyundai","mazda":"mazda","volkswagen":"volkswagen","bmw":"bmw","other makes":'others'};
    var sel_arr_year = {"all years":'all',"year >=2005":[2005,0],"year >=2010":[2010,0],"year >=2015":[2015,0],"year >=2016":[2016,0]};
    var sel_arr_price = {"all prices":'all',"USD <$5k":[2000,5000],"USD <$10k":[2000,10000],"USD $10k-15k":[10000,15000],"USD $15k-20k":[15000,20000],"USD $20k-25k":[20000,25000], "USD $25k-30k":[25000,30000]};
    var sel_arr_mileage = {"all mileages":'all', "miles <50k":[5000,50000],"miles <100k":[5000,100000],"miles <150k":[5000,150000]};
    var sel_arr_title = {"all title status":"all","clean title":"clean","other title status":"others"};
    var sel_arr_type = {"all types":"all","suv":"suv","truck":"truck","van":"van","other types":"others"};
    var sel_arr_area = {"all areas":"all","east bay":"eby","north bay":"nby","south bay":"sby","peninsula":"pen","san francisco":"sfc","santa cruz":"scz"}

    var div_ids = ["#sortby_make","#sortby_year","#sortby_price","#sortby_mileage","#sortby_title","#sortby_type","#sortby_area"];
    var filter_num = div_ids.length;
    var all_sel_arr_types = [Object.keys(sel_arr_make), Object.keys(sel_arr_year), Object.keys(sel_arr_price), Object.keys(sel_arr_mileage), Object.keys(sel_arr_title), Object.keys(sel_arr_type), Object.keys(sel_arr_area)];
    var all_sels = new Array(filter_num);
    var all_options = new Array(filter_num);
    var current_visible_elements = show_car_num;

    for(i = 0; i < filter_num; i++) {
        all_sels[i] = d3.select(div_ids[i])
                 .append("select").on("change", function(){ sortit(); });
        all_options[i] = all_sels[i].selectAll("option").data(all_sel_arr_types[i]).enter().append("option")
                        .attr("value",function(d){return d;})
                        .text(function(d){return d;});
    }

    /*reset all filters, show all circles, hide tooltip*/
    d3.select("#reset_filter_div")
        .append("button")
        .attr("class", "btn btn-primary")
        .text("reset filters")
        .on('click', function(d){
            for(i = 0; i < filter_num; i++) {
                all_sels[i].property('selectedIndex','0');
            }
            all_node.style("visibility", "visible");
            div.transition()
                .duration(100)
                .style("opacity", 0);
            current_visible_elements = show_car_num;
            d3.select("#num_car_shown")
                .html(current_visible_elements);
            return;
        });

    /*data_src pass from Flask*/
    if(data_src === 'dgdg' || data_src === 'hertz') {
        all_sels[FILTER_TITLE].attr("disabled","true");
        all_sels[FILTER_AREA].attr("disabled","true");

        all_sels[FILTER_TITLE].style("visibility", "hidden");
        all_sels[FILTER_AREA].style("visibility", "hidden");
    }

    var sortit = function() {
        current_visible_elements = 0;
        var s_ids = new Array(filter_num);
        var opt_selected = new Array(filter_num);
        all_node.style("visibility", "hidden");
        div.transition()
            .duration(100)
            .style("opacity", 0);
        for(ix = 0; ix < filter_num; ix++) {
            //figure out which options are selected
            s_ids[ix] = all_sels[ix].property('selectedIndex');
            opt_selected[ix] = all_options[ix].filter(function (d, i) { return i === s_ids[ix]; }).datum();
        }
        all_node.filter(function (d, i) { return filterit(d, i, opt_selected);})
            .transition()
            .duration(1000)
            .style("visibility", "visible");
        d3.select("#num_car_shown")
            .html(current_visible_elements);
    };
    var filterit = function(d, i, opt_selected_fil) {
        //for one circle, all filters are true, then show
        var switch_opt;
        switch_opt = sel_arr_make[opt_selected_fil[FILTER_MAKE]];
        var make_is_true = false;
        switch (switch_opt) {
        case 'all':
            make_is_true = true;
            break;
        case 'others':
            var arr_make_keys = Object.keys(sel_arr_make);
            var arr_make = arr_make_keys.map(function(v) { return sel_arr_make[v]; });
            make_is_true = !isInArray(d['brand'], arr_make.slice(1, arr_make.length-1));
            break;
        default:
            if(d['brand'] === switch_opt){
                make_is_true = true;
            }
        }
        switch_opt = sel_arr_year[opt_selected_fil[FILTER_YEAR]];
        var year_is_true = false;
        switch (switch_opt) {
        case 'all':
            year_is_true = true;
            break;
        default:
            var year_range = switch_opt;
            if( d['year'] >= year_range[0] ){
                year_is_true = true;
            }
        }
        switch_opt = sel_arr_price[opt_selected_fil[FILTER_PRICE]];
        var price_is_true = false;
        switch (switch_opt) {
        case 'all':
            price_is_true = true;
            break;
        default:
            var price_range = switch_opt;
            if( d['price'] > price_range[0] && d['price'] <= price_range[1] ){
                price_is_true = true;
            }
        }
        switch_opt = sel_arr_mileage[opt_selected_fil[FILTER_MILEAGE]];
        var mileage_is_true = false;
        switch (switch_opt) {
        case 'all':
            mileage_is_true = true;
            break;
        default:
            var mileage_range = switch_opt;
            if( d['mileage'] > mileage_range[0] && d['mileage'] <= mileage_range[1] ){
                mileage_is_true = true;
            }
        }
        switch_opt = sel_arr_title[opt_selected_fil[FILTER_TITLE]];
        var title_is_true = false;
        switch (switch_opt) {
        case 'all':
            title_is_true = true;
            break;
        case 'clean':
            if( d['title_status'] == 'clean' ){
                title_is_true = true;
            }
            break;
        default:
            if( d['title_status'] != 'clean' ){
                title_is_true = true;
            }
        }
        switch_opt = sel_arr_type[opt_selected_fil[FILTER_TYPE]];
        var type_is_true = false;
        switch (switch_opt) {
        case 'all':
            type_is_true = true;
            break;
        case 'others':
            var arr_type_keys = Object.keys(sel_arr_type);
            var arr_type = arr_type_keys.map(function(v) { return sel_arr_type[v]; });
            type_is_true = !isInArray(d['car_type'], arr_type.slice(1, arr_type.length-1));
            break;
        default:
            if(d['car_type'] === switch_opt){
                type_is_true = true;
            }
        }
        switch_opt = sel_arr_area[opt_selected_fil[FILTER_AREA]];
        var area_is_true = false;
        switch (switch_opt) {
        case 'all':
            area_is_true = true;
            break;
        default:
            if(d['place_area'] === switch_opt){
                area_is_true = true;
            }
        }
        var return_val = (make_is_true && year_is_true && price_is_true && mileage_is_true &&
                     title_is_true && type_is_true && area_is_true);
        if( return_val === true ) {
            current_visible_elements ++;
        }
        return (return_val);
    };  //filterit
    return;
}  //create_bubble_chart

function show_ufindcar() {
    if(mydataset.length > 0){
//        console.log(dataset);
        create_bubble_chart(mydataset);
    }else{
        console.log("Empty dataset!");
    }
}

