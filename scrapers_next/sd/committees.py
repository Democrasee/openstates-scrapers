from spatula import JsonListPage, CSS, JsonPage, SelectorError, SkipItem, URL
from openstates.models import ScrapeCommittee


class CommitteeList(JsonListPage):

    source_string = "https://sdlegislature.gov/api/SessionCommittees/Session/68"
    source = URL(source_string)

    def standardize_chamber(self, original_chamber_text):
        match original_chamber_text:
            case "H":
                return "lower"
            case "S":
                return "upper"
            case "J":
                return "legislature"
            case _:
                self.skip()


    def process_item(self, item):
        committee_json = item["Committee"]

        # The Full House & Senate are included in the json, tagged with the following property
        if committee_json['FullBody']: self.skip()

        com_id = item["SessionCommitteeId"]
        detail_link = f"https://sdlegislature.gov/api/SessionCommittees/Detail/{com_id}"
        homepage = f"https://sdlegislature.gov/Session/Committee/{com_id}/Detail"

        # try:
        #     title_div = (
        #         item.getchildren()[0]
        #         .getchildren()[0]
        #     )
        # except:
        #     self.skip()

        # try:
        #     chamber = title_div.getchildren()[0].text_content()
        # except:
        #     self.skip()

        # committee_name = item.text_content()

        com = ScrapeCommittee(
            name=committee_json['Name'],
            chamber=self.standardize_chamber(committee_json['Body'])
        )

        com.add_source(self.source_string)
        com.add_source(detail_link)
        com.add_link(homepage, note="homepage")

        return CommitteeDetail(com, source=URL(detail_link))

class CommitteeDetail(JsonPage):
    sample_source = URL("https://sdlegislature.gov/api/SessionCommittees/Detail/1156")

    def process_page(self):
        com = self.input
        return com