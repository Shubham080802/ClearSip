# Beverage Catalog

ClearSip records packaged beverages sold in a specific market so consumers can inspect the label for the exact item in hand. It keeps a product's identity separate from a time-bound label.

## Language

**Manufacturer**:
The company responsible for a beverage family, such as The Coca-Cola Company or Monster Energy.
_Avoid_: Brand owner, company

**Beverage Family**:
A marketed line under a manufacturer, such as Coca-Cola or Monster Energy.
_Avoid_: Brand, product

**Beverage Variant**:
A named formula or flavor within a beverage family, such as Coca-Cola Zero Sugar or a specific flavor release.
_Avoid_: Drink, SKU

**Product Package**:
A sellable market-specific container of one beverage variant, identified by its GTIN when available; size and container type are part of its identity.
_Avoid_: Beverage, product

**Label Version**:
A sourced, dated representation of the Nutrition Facts and ingredient statement for one product package. It can be superseded when the formulation or package label changes.
_Avoid_: Current facts, recipe

**Source Record**:
The provenance metadata for a label version, including publisher, URL, market, access date, and verification status.
_Avoid_: Citation, link

**Assessment**:
Sourced educational context for a declared ingredient in one label version; it is not a universal health verdict or medical recommendation.
_Avoid_: Rating, good/bad label
