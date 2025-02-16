#include <iostream>
#if defined WIN32 || defined _WIN32 || defined _WIN64
#include <windows.h>
#ifndef TIME_POINT_TYPE
#define TIME_POINT_TYPE chrono::steady_clock::time_point
#endif
#else
#ifndef TIME_POINT_TYPE
#define TIME_POINT_TYPE chrono::system_clock::time_point
#endif
#endif
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <chrono>
#ifndef EXIT_SUCCESS
#define EXIT_SUCCESS 0
#endif
#ifndef EXIT_FAILURE
#define EXIT_FAILURE 1
#endif
#ifndef EOF
#define EOF (-1)
#endif
#ifndef NULL
#define NULL 0
#endif
#ifndef WINDOWS_MAX_PATH
#define WINDOWS_MAX_PATH 32762
#endif
using namespace std;
char path[WINDOWS_MAX_PATH + 1] = { 0 };


class KeywordSearch
{
private:
	vector<string> lines{};
	map<string, set<size_t>> dict{};
	
	bool getTxt(const string filePath)
	{
		try
		{
			ifstream fp = ifstream(filePath);
			if (fp.is_open())
			{
				string line{};
				while (!fp.eof())
				{
					getline(fp, line);
					this->lines.push_back(line);
				}
				if (!this->lines.empty() && this->lines[this->lines.size() - 1].empty()) // remove the empty line at the end of the file
					this->lines.pop_back();
				return true;
			}
			else
				return false;
		}
		catch (...)
		{
			return false;
		}
	}
	
public:
	static const size_t INVALID = (size_t)(-1);
	
	KeywordSearch() {}
	bool build(const string filePath)
	{
		if (!this->getTxt(filePath))
			return false;
		this->dict.clear();
		for (size_t i = 0; i < this->lines.size(); ++i)
		{
			const size_t pos = lines[i].find("\ttags: ");
			if (string::npos != pos)
			{
				stringstream tags(lines[i].substr(pos + 7));
				while (!tags.eof())
				{
					string tag{};
					getline(tags, tag, ',');
					if (this->dict.find(tag) == this->dict.end())
						this->dict[tag] = set<size_t>{ i };
					else
						this->dict[tag].insert(i);
				}
			}
		}
		cout << endl << "number of keywords: " << this->dict.size() << endl << endl << "frequencies:";
		for (map<string, set<size_t>>::iterator it = this->dict.begin(); it != this->dict.end(); ++it)
			cout << " [" << it->first << ": " << it->second.size() << "]";
		cout << endl << endl;
		return true;
	}
	size_t kwSearchRaw(int argc, char* argv[])
	{
		if (argc >= 1)
		{
			vector<size_t> results{};
			const size_t lineCount = this->lines.size();
			const TIME_POINT_TYPE startTime = chrono::high_resolution_clock::now();
			for (size_t idx = 0; idx < lineCount; ++idx)
			{
				size_t pos = this->lines[idx].find("\ttags: ");
				if (string::npos != pos)
				{
					vector<string> tags{};
					stringstream ss(this->lines[idx].substr(pos + 7));
					while (!ss.eof())
					{
						string tag{};
						getline(ss, tag, ',');
						tags.push_back(tag);
					}
					bool flag = true;
					for (int i = 1; i < argc; ++i)
						if (find(tags.begin(), tags.end(), argv[i]) == tags.end())
						{
							flag = false;
							break;
						}
					if (flag)
						results.push_back(idx);
				}
			}
			const long double timeDelta = (long double)(chrono::high_resolution_clock::now() - startTime).count() / 1000000000;
			cout << "kwSearchRaw: " << results.size() << " result(s), cost = " << fixed << timeDelta << " second(s)" << endl;
			for (const size_t& idx : results)
				cout << this->lines[idx] << endl;
			cout << endl;
			return results.size();
		}
		else
			return INVALID;
	}
	size_t kwSearchIF(int argc, char* argv[])
	{
		if (argc >= 1)
		{
			const TIME_POINT_TYPE startTime = chrono::high_resolution_clock::now();
			if (1 == argc)
			{
				vector<size_t> results{};
				const size_t length = this->lines.size();
				for (size_t idx = 0; idx < length; ++idx)
					results.push_back(idx);
				const long double timeDelta = (long double)(chrono::high_resolution_clock::now() - startTime).count() / 1000000000;
				cout << "kwSearchIF: " << results.size() << " result(s), cost = " << fixed << timeDelta << " second(s)" << endl;
				for (const size_t& idx : results)
					cout << this->lines[idx] << endl;
				cout << endl;
				return results.size();
			}
			else
			{
				set<size_t> s = this->dict.find(argv[1]) != this->dict.end() ? this->dict[argv[1]] : set<size_t>{};
				for (int i = 2; i < argc && !s.empty(); ++i)
					if (this->dict.find(argv[i]) != this->dict.end())
					{
						set<size_t> tmp{};
						set_intersection(s.begin(), s.end(), this->dict[argv[i]].begin(), this->dict[argv[i]].end(), inserter(tmp, tmp.end()));
						s = tmp;
					}
					else
					{
						s.clear();
						break;
					}
				const long double timeDelta = (long double)(chrono::high_resolution_clock::now() - startTime).count() / 1000000000;
				cout << "kwSearchIF: " << s.size() << " result(s), cost = " << fixed << timeDelta << " second(s)" << endl;
				for (const size_t& idx : s)
					cout << this->lines[idx] << endl;
				cout << endl;
				return s.size();
			}
		}
		else
			return INVALID;
	}
};


#if defined WIN32 || defined _WIN32 || defined _WIN64
static bool cdCurrentDirectory()
{
	GetModuleFileNameA(NULL, path, WINDOWS_MAX_PATH);
	const string::size_type pos = string(path).find_last_of("\\/");
	if (string::npos != pos)
	{
		const string dir = string(path).substr(0, pos + 1); // to remain the path separator to avoid paths like "C:\\"
		SetCurrentDirectoryA(dir.c_str());
		GetCurrentDirectoryA(MAX_PATH, path);
#ifdef _DEBUG
		cout << "The working directory has been changed to \"" << path << "\". " << endl;
#endif
		return true;
	}
	else
		return false;
}
#endif

static int pressAnyKeyToContinue()
{
	rewind(stdin);
	fflush(stdin);
	cout << "The program is about to exit. Please press any key to continue. " << endl;
	return getchar();
}



int main(int argc, char* argv[]) // organic "late night"
{
	if (argc < 2)
	{
		cout << "Please provide the keywords for searching via the command line. " << endl;
		pressAnyKeyToContinue();
		return EOF;
	}
#if defined WIN32 || defined _WIN32 || defined _WIN64
	cdCurrentDirectory();
	const UINT currentConsoleOutputCP = GetConsoleOutputCP(); // backup the active code page
	if (!SetConsoleOutputCP(65001))
		cout << "Warning: As the file is encoded by UTF-8 while the program fails to change the active code page of the current console to 65001, the display may be incorrect. " << endl;
#endif
	KeywordSearch keywordSearch{};
	if (!(keywordSearch.build("Restaurants_London_England.tsv") || keywordSearch.build("../../Restaurants_London_England.tsv") || keywordSearch.build("../../../Restaurants_London_England.tsv")))
	{
		cout << "Cannot read the file \"Restaurants_London_England.tsv\". " << endl;
		pressAnyKeyToContinue();
		return EOF;
	}
	const size_t flagRaw = keywordSearch.kwSearchRaw(argc, argv), flagIF = keywordSearch.kwSearchIF(argc, argv);
#if defined WIN32 || defined _WIN32 || defined _WIN64
	SetConsoleOutputCP(currentConsoleOutputCP); // restore the active code page
#endif
	pressAnyKeyToContinue();
	return flagRaw != KeywordSearch::INVALID && flagIF != KeywordSearch::INVALID && flagRaw > 0 && flagIF > 0 && flagRaw == flagIF ? EXIT_SUCCESS : EXIT_FAILURE;
}