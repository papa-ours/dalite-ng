/** Recount search results
 *  @function
 */
export function recountResults() {
  $(".search-set").each(function() {
    $(this).find(".filter-count").empty().append($(this).find(".mdc-card:visible").length);
  });
}

/** Filter search results
 *  @function
 *  @param {String} el
 */
export function filter(el) {
  if ($(el).hasClass("mdc-chip--selected")) {
    $(el).removeClass("mdc-chip--selected");
  } else {
    $(el).addClass("mdc-chip--selected");
  }

  if ($(".mdc-chip--selected").length == 0) {
    $("#reset-filters").attr("disabled", true);
  }

  $("#search_results .mdc-card").css("display", "block");

  $("#search_results .mdc-card").each(function() {
    let card = this;
    $("#filter-on-category").find(".mdc-chip--selected").each(function() {
      if (card.getAttribute("category").toLowerCase().indexOf(this.getAttribute("c").toLowerCase()) < 0 ) {
        $(card).css("display", "none");
        $("#reset-filters").attr("disabled", false);
      }
    });

    $("#filter-on-discipline").find(".mdc-chip--selected").each(function() {
      if (card.getAttribute("discipline").slice(1, -1).toLowerCase() != this.getAttribute("d").toLowerCase()) {
        $(card).css("display", "none");
        $("#reset-filters").attr("disabled", false);
      }
    });
  });

  recountResults();
}

/** Reset filters
 *  @function
 */
export function reset() {
  $("#search_results .mdc-card").each(function() {
    $(this).css("display", "block");
    $(".mdc-chip").removeClass("mdc-chip--selected");
    $("#reset-filters").attr("disabled", true);
  });

  recountResults();
}

/** Process response for required filters
 *  @function
 */
export function processResponse() {
  bundle.toggleImages();
  bundle.toggleAnswers();

  $("#search-bar").attr("disabled", false);
  $("#progressbar").addClass("mdc-linear-progress--closed");

  // Add filters based on search results
  $("#filter-on-discipline").empty();
  $("#filter-on-category").empty();

  let disciplineList = [];
  $("#filter-on-discipline").append("<div class='mdc-chip-set mdc-chip-set--filter' data-mdc-auto-init='MDCChipSet'></div>");
  $("#search_results .mdc-card").each(function(index) {
    let d = this.getAttribute("discipline");
    if (!disciplineList.includes(d) & d.slice(1, -1) != "None") {
      disciplineList.push(d);
      $("#filter-on-discipline .mdc-chip-set").append("<div d="+d+" class='mdc-chip' onclick='search.filter(this)' tabindex='0' data-mdc-auto-init='MDCChip'>\
        <div class='mdc-chip__checkmark' >\
          <svg class='mdc-chip__checkmark-svg' viewBox='-2 -3 30 30'>\
            <path class='mdc-chip__checkmark-path' fill='none' stroke='black'\
              d='M1.73,12.91 8.1,19.28 22.79,4.59'/>\
          </svg>\
        </div>\
        <div class='mdc-chip__text'>"+d.slice(1, -1)+"</div>\
        </div>");
    }
  });
  console.info(disciplineList);

  let categoryList = [];
  $("#filter-on-category").append("<div class='mdc-chip-set mdc-chip-set--filter'  data-mdc-auto-init='MDCChipSet'></div>");
  $("#search_results .mdc-card").each(function() {
    let c = this.getAttribute("category");
    let list = c.split(" ");
    $(list).each(function(i) {
      if (!categoryList.includes(list[i].toLowerCase()) & list[i] != "") {
        categoryList.push(list[i].toLowerCase());
        $("#filter-on-category .mdc-chip-set").append("<div c="+list[i]+" class='mdc-chip' onclick='search.filter(this)' tabindex='0' data-mdc-auto-init='MDCChip'>\
          <div class='mdc-chip__checkmark' >\
            <svg class='mdc-chip__checkmark-svg' viewBox='-2 -3 30 30'>\
              <path class='mdc-chip__checkmark-path' fill='none' stroke='black'\
                d='M1.73,12.91 8.1,19.28 22.79,4.59'/>\
            </svg>\
          </div>\
          <div class='mdc-chip__text'>"+list[i]+"</div>\
          </div>");
      }
    });
  });
  console.info(categoryList);

  if ((disciplineList.length > 1 || categoryList.length > 1) && $("#search_results .mdc-card").length > 1) {
    $("#filters").css("display", "block");
    window.location.href = "#filters";
  } else {
    window.location.href = "#search_results";
  }
  if (disciplineList.length > 1) {
    $("#discipline-filters").css("display", "block");
  }
  if (categoryList.length > 1) {
    $("#category-filters").css("display", "block");
  }

  [].forEach.call(document.querySelectorAll(".mdc-chip"), el => {
    bundle.chips.MDCChip.attachTo(el);
  });

  [].forEach.call(document.querySelectorAll(".mdc-chip-set"), el => {
    bundle.chips.MDCChipSet.attachTo(el);
  });

  [].forEach.call(document.querySelectorAll(".mdc-icon-toggle"), el => {
    bundle.iconToggle.MDCIconToggle.attachTo(el);
  });

  [].forEach.call(document.querySelectorAll("#search_results .mdc-card"), el => {
    bundle.difficulty(el.getAttribute("matrix").replace(/'/g, "\""), el.id);
  });

  $(".analytics-tags").css("cursor", "default");
}

/** Set up search
 *  @function
 */
export function setupSearch() {
  $("#search_results").empty();
  $("#filters").css("display", "none");
  $("#show-discipline-filters").css("display", "none");
  $("#show-category-filters").css("display", "none");
  $("#search-bar").attr("disabled", true);
  $("#progressbar").removeClass("mdc-linear-progress--closed");
  window.location.href = "#progressbar";
}

/** Initialize likes
 *  @function
 */
export function initFavourites() {
  [].forEach.call(document.querySelectorAll(".mdc-icon-toggle"), el => {
    bundle.iconToggle.MDCIconToggle.attachTo(el);
  });
}
