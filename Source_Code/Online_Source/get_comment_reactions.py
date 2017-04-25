# Get Comment, Reactions, Reaction Counts
# For each comment url, a browser will be opened and the reaction buttion will be clicked automatically.
# After getting the data, the borwser will be closed.
from selenium import webdriver
import time
import re
import collections
import json
import unidecode
import datetime

image_reaction_map = {
                       "B9CMO5aR": 'funny',
                       "CYVHcC0N":'like',
                       "0cm0eNFD":'disagree',
                       "OQlF5Uky":'sad',
                       "yQIVy5qm":'wow',
                       "all":'all'
                     }

def get_reaction(img_str):
    img_ptn = 'https://assets.civilcomments.com/v1/images/reactions/(\w+)_64.png'
    reaction = image_reaction_map[re.match(img_ptn, img_str).group(1)]
    return reaction


def main():
    comment_urls = []
    # all_base_urls = "../../resources/test_urls.txt"   # on my machine
    # error_comment_reactions = "../../output/error_comment_reactions.txt"   # on my machine
    all_base_urls = "/Users/devadmin/Documents/SFU_comments_extractor/resources/missing_comments.txt"
    error_comment_reactions = "/Users/devadmin/Documents/SFU_comments_extractor/output/error_comment_reactions.txt"
    with open(all_base_urls) as base_input:
        for r in base_input:
            comment_urls.append(r.replace("\n", "")+"comments/")
    article_id_ptn = "http://www.theglobeandmail.com/.*?/article(\d+)/comments"


    for comment_url in comment_urls:
        # driver = webdriver.Firefox()  # my machine
        driver = webdriver.Firefox(executable_path='/Users/devadmin/Documents/geckodriver')
        driver.get(comment_url)
        driver_session_id = driver.session_id
        if driver_session_id == None:
            with open(error_comment_reactions, 'a') as error_output:
                error_output.write(comment_url+"\n")
            driver.quit()
        time.sleep(5)
        try:
            article_id = re.match(article_id_ptn, comment_url).group(1)
            all_dct = {}

            show_more_click = ""
            while(show_more_click != None):
                try:
                    show_more_click = driver.find_element_by_css_selector('.ciTTYMA.c3el1TK')
                    driver.execute_script("arguments[0].scrollIntoView();", show_more_click)
                    show_more_click.click()
                    time.sleep(3)
                except:
                    break


            whole_comment_lst = driver.find_elements_by_class_name("c3DcHfc")
            for whole_comment in whole_comment_lst:
                whole_comment_key = str(datetime.datetime.now().time())[9:]
                all_dct.setdefault(whole_comment_key, {"author":"", "post_time":"", "text":"", "reactions":{},
                                                       "replies":[]})

                comments = whole_comment.find_elements_by_class_name("c2LlVA7")
                author_count = 0
                post_time_count = 0
                text_count = 0
                reaction_count = 0
                is_first = 1
                for comment in comments:
                    comment_author = ""
                    comment_post_time = ""
                    in_reply_to = ""
                    comment_text = ""
                    comment_reactions = {}

                    try:
                        comment_author = comment.find_element_by_class_name("c29cjTJ").text
                        author_count += 1
                    except:
                        author_count += 1
                        pass
                    try:
                        comment_post_time = comment.find_element_by_class_name("cNCPihY").text
                        post_time_count += 1
                    except:
                        post_time_count += 1
                        pass
                    try:
                        in_reply_to = unidecode.unidecode(comment.find_element_by_class_name("cxpl-23").text
                                                       .replace("\n", "").replace("\"", "'")).replace("\"", "'")
                    except:
                        pass
                    try:
                        if in_reply_to == "":
                            comment_text = unidecode.unidecode(comment.find_element_by_class_name("c1bE414").text
                                                               .replace("\n", "").replace("\"", "'")).replace("\"", "'")
                        else:
                            comment_text = "(" + in_reply_to + ") " + \
                                           unidecode.unidecode(comment.find_element_by_class_name("c1bE414").text
                                                               .replace("\n", "").replace("\"", "'")).replace("\"", "'")
                        text_count += 1
                    except:
                        text_count += 1
                        pass

                    try:
                        reactions_click = comment.find_element_by_class_name("c2iexvC")
                        driver.execute_script("arguments[0].scrollIntoView();", reactions_click)
                        reactions_click.click()

                        reaction_counts = [rc.text for rc in driver.find_elements_by_class_name('c2oytXt')]
                        reaction_users = [ru.text for ru in driver.find_elements_by_class_name('c3TwkwL')]
                        reaction_time = [rt.text for rt in driver.find_elements_by_class_name('c_0Qpsz')]
                        reactions = [get_reaction(r.get_attribute('src')) for r in driver.find_elements_by_class_name('c3S62yx')]
                        reactions = reactions[len(reaction_counts):]
                        reaction_lst = []

                        for i in range(len(reaction_users)):
                            reaction_lst.append({'reaction_user':reaction_users[i], 'reaction_time':reaction_time[i], 'reaction':reactions[i]})

                        comment_reactions = collections.OrderedDict({'reaction_counts':reaction_counts, 'reaction_list':reaction_lst})
                        reaction_count += 1

                        close_clk = driver.find_element_by_class_name("c1KbZcP")
                        close_clk.click()
                    except:
                        reaction_count += 1
                        pass

                    if is_first == 1:
                        all_dct[whole_comment_key]["author"] = comment_author
                        all_dct[whole_comment_key]["post_time"] = comment_post_time
                        all_dct[whole_comment_key]["text"] = comment_text
                        all_dct[whole_comment_key]["reactions"] = comment_reactions
                        is_first = 0
                    else:
                        reply_dct = {"author":comment_author, "post_time":comment_post_time,
                                     "text":comment_text, "reactions":comment_reactions}
                        all_dct[whole_comment_key]["replies"].append(reply_dct)

                if author_count != post_time_count or post_time_count!= text_count or reaction_count != text_count:
                    with open(error_comment_reactions, 'a') as error_output:
                         error_output.write("counts not match: (" + author_count + ", " + post_time_count + ", " + \
                                            text_count + ", " + reaction_count + ")" + comment_url + "\n")
                    driver.quit()
                    time.sleep(5)
                    return

            if len(all_dct) == 0:
                # f_name = r'../../output/empty_comment_ids.txt'  # my machine
                f_name = '/Users/devadmin/Documents/SFU_comments_extractor/output/empty_comment_ids.txt'
                with open(f_name, 'a') as out:
                    out.write(article_id+"\n")
                print("test if", article_id)
                driver.quit()
                time.sleep(5)

            else:
                # f_name = r'../../output/Comment_Reactions/article_' + article_id + '_comments.json'  # my machine
                f_name = '/Users/devadmin/Documents/SFU_comments_extractor/output/Comment_Reactions/article_' + article_id + '_comments.json'
                with open(f_name, 'w') as out:
                    json.dump(collections.OrderedDict(all_dct), out)
                print("test else", article_id)
                driver.quit()
                time.sleep(5)

        except:
            with open(error_comment_reactions, 'a') as error_output:
                error_output.write(comment_url+"\n")
            driver.quit()
            time.sleep(5)


if __name__ == "__main__":
    main()