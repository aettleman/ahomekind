// Shared "who gets your money" ownership data. Originally lived only on
// the learn page as its own tab; now surfaced per-brand inside the "why"
// disclosure on brand-check.html instead, since that is the moment it is
// actually useful -- while someone is looking at one specific brand.
// A hand-curated list on purpose, not automated from brand.parentCompany:
// ownership changes fast and a wrong claim here is worse than none, so
// only checked, written entries go in.
var AHK_OWNERS = [
{ parent: "SC Johnson", clean: false, cf: ["Method", "Ecover"], other: ["Glade", "Windex", "Mr Muscle", "Duck", "Raid", "Pledge"], note: "Both Method and Ecover are Leaping Bunny certified and vegan in their own right. The parent company is not cruelty-free." },
{ parent: "Unilever", clean: false, cf: ["Simple"], other: ["Dove", "Vaseline", "Pond's", "Nexxus", "TIGI", "REN", "Murad", "Hourglass", "Seventh Generation"], note: "Simple is PETA certified. Unilever as a whole is not a cruelty-free company." },
{ parent: "L'Oreal", clean: false, cf: ["Garnier"], other: ["Maybelline", "NYX", "Lancome", "La Roche-Posay", "CeraVe", "Kiehl's", "Urban Decay", "Essie", "Vichy", "YSL Beauty", "Redken", "SkinCeuticals", "IT Cosmetics"], note: "Garnier is Leaping Bunny certified and not sold in mainland China. L'Oreal still tests where legally required elsewhere." },
{ parent: "Coty", clean: false, cf: ["Rimmel"], other: ["Bourjois", "Max Factor", "Sally Hansen", "CoverGirl", "OPI", "Wella", "Clairol", "Philosophy"], note: "Rimmel holds Leaping Bunny certification. Only its Kind and Free range is fully vegan." },
{ parent: "Walgreens Boots Alliance", clean: false, cf: ["No7"], other: ["Boots own brand", "Soap and Glory", "Botanics"], note: "No7 is cruelty-free and not sold in mainland China stores. Not fully vegan, some products contain lanolin, carmine or beeswax." },
{ parent: "Independent, no conflicting parent", clean: true, cf: ["e.l.f. Cosmetics", "Faith in Nature", "Barry M", "Astonish", "The Pink Stuff", "BYOMA"], other: [], note: "These are not owned by a company that tests on animals. Every pound goes to a business whose whole output is cruelty-free." }
];

// Looks a brand name up against AHK_OWNERS (case-insensitive, matches
// either its cf or other lists) and returns the owning entry, or null.
function ahkFindOwner(brandName){
  var n = (brandName || '').toLowerCase().trim();
  for (var i = 0; i < AHK_OWNERS.length; i++){
    var o = AHK_OWNERS[i];
    var all = o.cf.concat(o.other);
    for (var j = 0; j < all.length; j++){
      if (all[j].toLowerCase() === n) return o;
    }
  }
  return null;
}
