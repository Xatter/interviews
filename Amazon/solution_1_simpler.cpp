//
//  main.cpp
//  Amazon
//
//  Created by Jim Wallace on 6/29/14.
//  Copyright (c) 2014 Jim Wallace. All rights reserved.
//


/*
 Given a list of strings, write a function which returns a list of list
 of strings, where each list contains the strings which are anagrams of
 each other.
 
 E.g. Given the input
 [ "cat", "dog", "god", "atc", "door", "gdo" ]
 return
 [ [ "cat", "atc" ], [ "dog", "god", "gdo" ], [ "door" ] ].
 
 
 "dor" is NOT an anogram of "door"

 Unfortunately on the phone I came up with the n^2 brute force solution where you look at
 each word, and then look at all the other words and create the lists.  Sad panda.
 
 About 5 minutes after my interview while walking on the street this solution popped into my head.
 
 It's Nlog(N) but uses a lot of memory. I still think there might be a linear solution.
 */

#include <iostream>
#include <vector>
#include <unordered_map>

int main(int argc, const char * argv[]) {
    std::vector<std::string> list;
    list.push_back("cat");
    list.push_back("dog");
    list.push_back("god");
    list.push_back("atc");
    list.push_back("door");
    list.push_back("gdo");
    
    std::unordered_map<std::string, std::vector<std::string>*> hash;
    
    for (auto i = list.begin(); i!=list.end(); ++i) {
        std::string str = *i;
        std::string sorted_str = *i;
        std::sort(sorted_str.begin(), sorted_str.end());
        
        if(hash[sorted_str] == NULL) {
            hash[sorted_str] = new std::vector<std::string>();
        }
        
        hash[sorted_str]->push_back(str);
    }
    
    for (auto kvp : hash) {
        auto vec = std::get<1>(kvp);
        std::cout << "[";
        for (auto str : *vec) {
            std::cout << str << ",";
        }
        std::cout << "]";
    }
    
    return 0;
}
