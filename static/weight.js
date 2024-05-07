goal_direction_text = document.querySelector(".goal-direction");
input_current_weight = document.getElementsByName("current weight")[0];
input_goal_weight = document.getElementsByName("goal weight")[0];
current_weight = goal_weight = 0;

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