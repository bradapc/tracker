//Weight text gain/loss update based on current vs goal weight differential.
goal_direction_text = document.querySelector(".goal-direction");
input_current_weight = document.getElementsByName("current weight")[0];
input_goal_weight = document.getElementsByName("goal weight")[0];
current_weight = goal_weight = 0;
goal_step_text = document.querySelector(".goal-step-text");
height_div_metric = document.getElementById("metric-height-div");
height_div_imperial = document.getElementById("imperial-height-div");

input_current_weight.addEventListener("input", function() {
    current_weight = input_current_weight.value;
    current_weight = parseFloat(current_weight);
    updateGoalText();
});

input_goal_weight.addEventListener("input", function() {
    goal_weight = input_goal_weight.value;
    goal_weight = parseFloat(goal_weight);
    updateGoalText();
})

function updateGoalText() {
    if (current_weight && goal_weight) {
        if (current_weight > goal_weight) {
            goal_direction_text.innerHTML = "lose";
        }
        else {
            goal_direction_text.innerHTML = "gain";
        }
    }
}

//Unit swapper
metric_radio = document.getElementById("metric");
imperial_radio = document.getElementById("imperial");

function swapUnits(weight_unit, height_unit) {
    input_current_weight.placeholder = "current weight " + "(" + weight_unit + ")";
    input_goal_weight.placeholder = "goal weight " + "(" + weight_unit + ")";
    goal_step_text.innerHTML = weight_unit + "/week";
    if (height_unit == "cm") {
        height_div_metric.style.display = "inline-block";
        height_div_imperial.style.display = "none";
    }
    else if(height_unit == "ft in") {
        height_div_metric.style.display = "none";
        height_div_imperial.style.display = "inline-block";
    }
}

function checkUnitSwap(){
    if (metric_radio.checked) {
        swapUnits("kg", "cm");
    }
    else if (imperial_radio.checked) {
        swapUnits("lb", "ft in");
    }
}

checkUnitSwap();