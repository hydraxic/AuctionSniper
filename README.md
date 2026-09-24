<!-- ABOUT THE PROJECT -->
## About The Project

**This project has not been maintained since July 2023.**

AuctionSniper is a program that searches for items listed on the Auction House in the online video game *Hypixel Skyblock* for a price much lower than its actual value. Profitable flips are regularly posted to the Discord server (NO LONGER MAINTAINED).

<!-- GETTING STARTED -->
## Usage

To see flips posted, join the Discord server. The source code can be freely downloaded and run locally, although modifications must be made.

## Details

This project was started in February of 2022, and has been archived as of July 2023.

The program asynchronously and periodically searches for items in which the listed BIN (Buy It Now) price is lower by a threshold to its estimated value, where its value is determined by:
* other price listings of the same item;
* other price listings of the same *base* item (the item with any modifiers removed);
* modifiers applied to the item, which may increase or lower the value;
* popularity or meta, where listings for common items which will rarely sell may inaccurately reflect value, or items which are heavily sought after and may increase value; and
* specific combinations of item and modifiers which greatly increase value;

The program pulls data from Hypixel's public API as well as baseline lowest BIN pricing from Moulberry's BIN API (`moulberry.codes/lowestbin.json` - this external project is also no longer maintained).

Flips found are automatically published to the public Discord server.

The project was deployed with the free tier Amazon Web Services (AWS) using an EC2 compute instance. 

## Achievements

The Discord server has reached a peak of 1,000 members!
