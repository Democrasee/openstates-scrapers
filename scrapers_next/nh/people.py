from spatula import URL, CsvListPage, HtmlPage, CSS, XPath
from openstates.models import ScrapePerson
from dataclasses import dataclass
import re


@dataclass
class PartialPerson:
    name: str
    chamber: str
    district: str
    source: str


# 418 total
# 24 total senators
# total representatives


class SenDetail(HtmlPage):
    input_type = PartialPerson

    def process_page(self):

        party = CSS("span.MemberHeader").match_one(self.root).text_content().strip()
        party = re.search(r"(.+)\(([A-Z])-.+\)", party).groups()[1]
        print(party)

        p = ScrapePerson(
            name=self.input.name,
            state="nh",
            chamber=self.input.chamber,
            district=self.input.district,
            party=party,
        )

        p.add_source(self.input.source)
        p.add_source(self.source.url)
        p.add_link(self.source.url, note="homepage")

        img = CSS("img.auto-style2").match_one(self.root).get("src")
        p.image = img

        contact_info = XPath("//*[@id='page_content']/table/tr[2]/td//strong[3]").match(
            self.root
        )[0]
        cap_addr = contact_info.getnext().tail.strip()
        cap_addr += " "
        cap_addr += contact_info.getnext().getnext().tail.strip()
        cap_addr += " "
        cap_addr += contact_info.getnext().getnext().getnext().tail.strip()
        p.capitol_office.address = cap_addr

        # phone = XPath("//*[@id='page_content']/table/tr[2]/td//strong[4]").match(self.root)[0].tail.strip()
        # print(phone)
        # capitol_office.voice
        # education

        # some might be missing, most already have
        # party
        # email

        return p


class Legislators(CsvListPage):

    # house_profile_url = (
    #     "http://www.gencourt.state.nh.us/house/members/member.aspx?member={}"
    # )

    source = URL("http://gencourt.state.nh.us/downloads/members.txt")

    def process_item(self, item):
        for line in item.values():
            print(line)
            member = line.split("\t")

            lastname = member[0]
            firstname = member[1]
            middlename = member[2]
            name = firstname + " " + middlename + " " + lastname

            legislativebody = member[3]
            if legislativebody == "H":
                chamber = "lower"
            elif legislativebody == "S":
                chamber = "upper"

            district = member[6]

            # 39 out of 116 legislators have incomplete info (len(member) < 19)
            # 24 senators and 15 reps
            if chamber == "upper":
                if len(district) == 1:
                    district_id = "0" + district
                else:
                    district_id = district
                detail_link = f"http://www.gencourt.state.nh.us/Senate/members/webpages/district{district_id}.aspx"

                partial = PartialPerson(
                    name=name,
                    chamber=chamber,
                    district=district,
                    source=self.source.url,
                )

                return SenDetail(partial, source=detail_link)

            # print(len(member))
            if len(member) > 9:
                party = member[15]

                p = ScrapePerson(
                    name=name,
                    state="nh",
                    chamber=chamber,
                    district=district,
                    party=party,
                )

                # seat_num = member[4]

                p.add_source(self.source.url)

                county = member[5]
                if county != "":
                    p.extras["county"] = county

                address = member[8]

                address2 = member[9]
                city = member[10]
                zipcode = member[11]
                full_addr = (
                    address + " " + address2 + " " + city + ", New Hampshire" + zipcode
                )
                p.district_office.address = full_addr

                phone = member[13]
                p.district_office.voice = phone

                email = member[14]
                p.email = email

                gendercode = member[16]
                p.extras["gender code"] = gendercode
                title = member[17]
                p.extras["title"] = title

                return p
