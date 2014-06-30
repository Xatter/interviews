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
#include <array>

int main(int argc, const char * argv[]) {
    std::vector<std::string> list;
    list.push_back("cat");
    list.push_back("dog");
    list.push_back("god");
    list.push_back("atc");
    list.push_back("door");
    list.push_back("gdo");
    
    std::vector<std::tuple<std::array<int, 256>, std::string>> computed_pair;
    
    for (auto i = list.begin(); i!=list.end(); ++i) {
        std::array<int, 256> array{}; // ask for all of ASCII range, and set to 0 initially
        
        std::string word = *i;
        for (int j = 0; j<word.size(); j++) {
            array[(int)word[j]]++;  // Abstracts letters into a count array
        }
        
        auto pair = std::make_tuple(array, word);
        computed_pair.push_back(pair);
    }
    
    std::sort(computed_pair.begin(), computed_pair.end(),
              [&](std::tuple<std::array<int, 256>, std::string> a, std::tuple<std::array<int, 256>, std::string> b) {
                  std::array<int, 256> str_a = std::get<0>(a);
                  std::array<int, 256> str_b = std::get<0>(b);
                  
                  for (int i = 0; i<256; i++) {
                      if (str_a[i] == str_b[i]) {
                          continue;
                      } else {
                          return str_a > str_b ? 1 : -1;
                      }
                  }
                  return 0;
              });
    
    std::vector<std::vector<std::string>> output;
    
    int len = computed_pair.size();
//    for (auto pair : computed_pair) {
//        std::cout << std::get<1>(pair) << std::endl;
//    }
    
    for (int i = 0; i<len; i++) {
        auto current = computed_pair[i];
        auto current_key = std::get<0>(current);
        auto current_value = std::get<1>(current);
        
        std::vector<std::string> vec;
        vec.push_back(current_value);
        
        for (i+=1;i<len; i++) {
            auto next = computed_pair[i];
            auto next_key = std::get<0>(next);
            auto next_value = std::get<1>(next);
            
            bool is_equal = true;
            for (int j = 0; j<256; j++) {
                if (current_key[j] != next_key[j]) {
                    is_equal = false;
                    break;
                }
            }
            
            if (is_equal) {
                vec.push_back(next_value);
            } else {
                i--;
                break;
            }
        }
        output.push_back(vec);
    }
    
    // output results
    for (std::vector<std::string> vec : output) {
        std::cout << "[";
        for (std::string str : vec) {
            std::cout << str << ",";
        }
        std::cout << "], ";
    }
    
    return 0;
}
